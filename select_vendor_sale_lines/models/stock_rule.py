# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from dateutil.relativedelta import relativedelta
from itertools import groupby

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_buy(self, procurements):
        procurements_by_po_domain = defaultdict(list)
        for procurement, rule in procurements:

            # Get the schedule date in order to find a valid seller
            procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])
            schedule_date = (procurement_date_planned - relativedelta(days=procurement.company_id.po_lead))

            supplier = procurement.product_id.with_context(force_company=procurement.company_id.id)._select_seller(
                partner_id=procurement.values.get("supplier_id"),
                quantity=procurement.product_qty,
                date=schedule_date.date(),
                uom_id=procurement.product_uom)
            # supplier = procurement.
            # Fall back on a supplier for which no price may be defined. Not ideal, but better than
            # blocking the user.
            supplier = procurement.values.get('move_dest_ids').sale_line_id.selected_supplier_id
            supplier = supplier or procurement.product_id._prepare_sellers(False).filtered(
                lambda s: not s.company_id or s.company_id == procurement.company_id
            )[:1]

            if not supplier:
                msg = _('There is no matching vendor price to generate the purchase order for product %s (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.') % (procurement.product_id.display_name)
                raise UserError(msg)

            partner = supplier.name
            # we put `supplier_info` in values for extensibility purposes
            procurement.values['supplier'] = supplier
            procurement.values['propagate_date'] = rule.propagate_date
            procurement.values['propagate_date_minimum_delta'] = rule.propagate_date_minimum_delta
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            domain = rule._make_po_get_domain(procurement.company_id, procurement.values, partner)
            procurements_by_po_domain[domain].append((procurement, rule))

        for domain, procurements_rules in procurements_by_po_domain.items():
            # Get the procurements for the current domain.
            # Get the rules for the current domain. Their only use is to create
            # the PO if it does not exist.
            procurements, rules = zip(*procurements_rules)

            # Get the set of procurement origin for the current domain.
            origins = set([p.origin for p in procurements])
            # Check if a PO exists for the current domain.
            po = self.env['purchase.order'].sudo().search([dom for dom in domain], limit=1)
            company_id = procurements[0].company_id
            if not po:
                # We need a rule to generate the PO. However the rule generated
                # the same domain for PO and the _prepare_purchase_order method
                # should only uses the common rules's fields.
                vals = rules[0]._prepare_purchase_order(company_id, origins, [p.values for p in procurements])
                # The company_id is the same for all procurements since
                # _make_po_get_domain add the company in the domain.
                # We use SUPERUSER_ID since we don't want the current user to be follower of the PO.
                # Indeed, the current user may be a user without access to Purchase, or even be a portal user.
                po = self.env['purchase.order'].with_context(force_company=company_id.id).with_user(SUPERUSER_ID).create(vals)
            else:
                # If a purchase order is found, adapt its `origin` field.
                if po.origin:
                    missing_origins = origins - set(po.origin.split(', '))
                    if missing_origins:
                        po.write({'origin': po.origin + ', ' + ', '.join(missing_origins)})
                else:
                    po.write({'origin': ', '.join(origins)})

            procurements_to_merge = self._get_procurements_to_merge(procurements)
            procurements = self._merge_procurements(procurements_to_merge)

            po_lines_by_product = {}
            grouped_po_lines = groupby(po.order_line.filtered(lambda l: not l.display_type and l.product_uom == l.product_id.uom_po_id).sorted(lambda l: l.product_id.id), key=lambda l: l.product_id.id)
            for product, po_lines in grouped_po_lines:
                po_lines_by_product[product] = self.env['purchase.order.line'].concat(*list(po_lines))
            po_line_values = []
            for procurement in procurements:
                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if po_line:
                    # If the procurement can be merge in an existing line. Directly
                    # write the new values on it.
                    vals = self._update_purchase_order_line(procurement.product_id,
                        procurement.product_qty, procurement.product_uom, company_id,
                        procurement.values, po_line)
                    po_line.write(vals)
                else:
                    # If it does not exist a PO line for current procurement.
                    # Generate the create values for it and add it to a list in
                    # order to create it in batch.
                    partner = procurement.values['supplier'].name
                    po_line_values.append(self._prepare_purchase_order_line(
                        procurement.product_id, procurement.product_qty,
                        procurement.product_uom, procurement.company_id,
                        procurement.values, po))
            self.env['purchase.order.line'].sudo().create(po_line_values)

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        partner = values['supplier'].name
        procurement_uom_po_qty = product_uom._compute_quantity(product_qty, product_id.uom_po_id)
        # _select_seller is used if the supplier have different price depending
        # the quantities ordered.
        seller = product_id.with_context(force_company=company_id.id)._select_seller(
            partner_id=partner,
            quantity=procurement_uom_po_qty,
            date=po.date_order and po.date_order.date(),
            uom_id=product_id.uom_po_id)
        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes, product_id, seller.name) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == company_id.id)

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, product_id.supplier_taxes_id, taxes_id, company_id) if seller else 0.0
        selected_supplier_id = values['move_dest_ids'].sale_line_id.selected_supplier_id
        price_unit = selected_supplier_id.price
        if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
            price_unit = seller.currency_id._convert(
                price_unit, po.currency_id, po.company_id, po.date_order or fields.Date.today())

        product_lang = product_id.with_prefetch().with_context(
            lang=partner.lang,
            partner_id=partner.id,
        )
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        date_planned = self.env['purchase.order.line']._get_date_planned(seller, po=po)

        return {
            'name': name,
            'product_qty': procurement_uom_po_qty,
            'product_id': product_id.id,
            'product_uom': product_id.uom_po_id.id,
            'price_unit': price_unit,
            'propagate_cancel': values.get('propagate_cancel'),
            'date_planned': date_planned,
            'propagate_date': values['propagate_date'],
            'propagate_date_minimum_delta': values['propagate_date_minimum_delta'],
            'orderpoint_id': values.get('orderpoint_id', False) and values.get('orderpoint_id').id,
            'taxes_id': [(6, 0, taxes_id.ids)],
            'order_id': po.id,
            'move_dest_ids': [(4, x.id) for x in values.get('move_dest_ids', [])],
        }