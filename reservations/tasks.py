from reservations.procedures.clear_crons import clear_old_reservations, clear_unavailable, clear_not_member, \
    set_end_date_if_no_lent_out


class ReservationCancel:
    def exec(self):
        clear_old_reservations()
        clear_unavailable()
        clear_not_member()
        set_end_date_if_no_lent_out()
