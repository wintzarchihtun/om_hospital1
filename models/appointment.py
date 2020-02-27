# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import pytz


class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "appointment_date desc"

    def delete_lines(self):
        for rec in self:
            # print("Time in UTC", rec.appointment_datetime)
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
            # print("user_tz", user_tz)
            date_today = pytz.utc.localize(rec.appointment_datetime).astimezone(user_tz)
            # print("Time in local Timezone...", date_today)
            rec.appointment_lines = [(5, 0, 0)]

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
        result = super(HospitalAppointment, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        # overriding the write method of appointment model
        res = super(HospitalAppointment, self).write(vals)
        print("Test write function")
        # do as per the need
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for rec in self:
            return {'domain': {'order_id': [('partner_id', '=', rec.partner_id.id)]}}

    name = fields.Char(string='Appointment ID', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    patient_age = fields.Integer('Age', related='patient_id.patient_age')
    notes = fields.Text(string="Registration Note")
    doctor_note = fields.Text(string="Note", track_visibility='onchange')
    appointment_lines = fields.One2many('hospital.appointment.lines', 'appointment_id', string='Appointment Lines')
    pharmacy_note = fields.Text(string="Note", track_visibility='always')
    appointment_date = fields.Date(string='Date')
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    appointment_date_end = fields.Date(string='End Date')
    appointment_datetime = fields.Datetime(string='Date Time')
    partner_id = fields.Many2one('res.partner', string="Customer")
    order_id = fields.Many2one('sale.order', string="Sale Order")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, default='draft')


class HospitalAppointmentLines(models.Model):
    _name = 'hospital.appointment.lines'
    _description = 'Appointment Lines'

    product_id = fields.Many2one('product.product', string='Medicine')
    product_qty = fields.Integer(string="Quantity")
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment ID')

