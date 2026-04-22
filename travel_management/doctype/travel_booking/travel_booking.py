import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, flt

class TravelBooking(Document):
    def validate(self):
        # 1. Calculations
        self.calculate_totals()
        
        # 2. Date Validations
        self.validate_dates()
        
        # 3. Financial Validations
        self.validate_payments()
        
        # 4. Status Rules
        self.validate_status_rules()

    def calculate_totals(self):
        """
        Calculates Total Amount from Child Table and determines Balance.
        """
        total = 0
        for item in self.get("booking_items"):
            total += flt(item.selling_price)
        
        self.total_amount = total
        self.balance_amount = flt(self.total_amount) - flt(self.advance_paid)

    def validate_dates(self):
        """
        Validates the sequence of Booking and Travel dates.
        """
        if not self.booking_date:
            return

        if self.travel_start_date:
            if getdate(self.travel_start_date) < getdate(self.booking_date):
                frappe.throw(_("Travel Start Date must be on or after Booking Date"))
        
        if self.travel_end_date and self.travel_start_date:
            if getdate(self.travel_end_date) < getdate(self.travel_start_date):
                frappe.throw(_("Travel End Date must be on or after Travel Start Date"))

    def validate_payments(self):
        """
        Ensures Advance Paid is logically sound.
        """
        if flt(self.advance_paid) > flt(self.total_amount):
            frappe.throw(_("Advance Paid must not exceed Total Amount"))

    def validate_status_rules(self):
        """
        Implements specific status transition logic.
        """
        # Rule: Cannot be Confirmed without Advance Paid
        if self.status == "Confirmed" and flt(self.advance_paid) <= 0:
            frappe.throw(_("Booking cannot be marked as Confirmed unless Advance Paid is greater than zero"))
        
        # Rule: Completed bookings cannot be cancelled
        # We check the status currently in the database (before this save)
        if self.get_db_value("status") == "Completed" and self.status == "Cancelled":
            frappe.throw(_("Completed bookings cannot be cancelled"))
