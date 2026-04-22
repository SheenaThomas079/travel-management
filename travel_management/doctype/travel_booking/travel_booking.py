import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class TravelBooking(Document):
    def validate(self):
        self.calculate_totals()
        self.run_validations()

    def calculate_totals(self):
        # 1. Total Amount = Sum of Selling Price
        self.total_amount = sum(float(item.selling_price or 0) for item in self.booking_items)
        
        # 2. Balance Amount = Total Amount – Advance Paid
        self.balance_amount = self.total_amount - (float(self.advance_paid or 0))

    def run_validations(self):
        # 1. Date Validations
        if self.travel_start_date and self.booking_date:
            if getdate(self.travel_start_date) < getdate(self.booking_date):
                frappe.throw(_("Travel Start Date must be on or after Booking Date"))
        
        if self.travel_end_date and self.travel_start_date:
            if getdate(self.travel_end_date) < getdate(self.travel_start_date):
                frappe.throw(_("Travel End Date must be on or after Travel Start Date"))

        # 2. Advance Paid Validation
        if float(self.advance_paid or 0) > self.total_amount:
            frappe.throw(_("Advance Paid must not exceed Total Amount"))

        # 3. Status Rule: Advance Paid > 0 for Confirmed
        if self.status == "Confirmed" and float(self.advance_paid or 0) <= 0:
            frappe.throw(_("Booking cannot be marked as Confirmed unless Advance Paid is greater than zero"))
        
        # 4. Status Rule: Completed cannot be Cancelled (Checked during save)
        if self.get_db_value("status") == "Completed" and self.status == "Cancelled":
            frappe.throw(_("Completed bookings cannot be cancelled"))
