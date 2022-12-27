import algosdk
from pyteal import *


class CarSharingContract:
    class Constants:
        escrow_min_balance = Int(1000000)

    class Variables:
        # Global State Keys
        creator_address = Bytes("creator")  # Bytes
        creator_name = Bytes("creator_name")  # Bytes
        departure_address = Bytes("departure_address")  # Bytes
        arrival_address = Bytes("arrival_address")  # Bytes
        departure_date = Bytes("departure_date")  # Bytes
        departure_date_round = Bytes("departure_date_round")  # Int
        arrival_date = Bytes("arrival_date")  # Bytes
        arrival_date_round = Bytes("arrival_date_round")  # Int
        max_capacity = Bytes("max_capacity")  # Int
        trip_unit_cost = Bytes("trip_unit_cost")  # Int
        app_state = Bytes("trip_state")  # Int
        trip_capacity = Bytes("trip_capacity")  # Int
        escrow_address = Bytes("escrow_address")  # Bytes
        # Local State Keys
        book_capacity = Bytes("book_capacity")  # Int

    class AppMethods:
        initialize_escrow = "initializeEscrow"
        fund_escrow = "fundEscrow"
        update_trip = "updateTrip"
        participate_trip = "participateTrip"
        start_trip = "startTrip"
        cancel_trip_participation = "cancelParticipation"

    class AppState:
        not_initialized = Int(0)
        initialized = Int(1)
        ready = Int(2)
        finished = Int(3)

    class UserState:
        participating = Int(1)
        not_participating = Int(0)

    def application_start(self):
        """
        Start the application, check with transaction to execute
        :return:
        """
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)

        handle_noop = Seq(
            Cond(
                [Txn.application_args[0] == Bytes(self.AppMethods.initialize_escrow),
                 self.initialize_escrow(escrow_address=Txn.application_args[1])],

                [Txn.application_args[0] == Bytes(self.AppMethods.fund_escrow),
                 self.fund_escrow()],

                [Txn.application_args[0] == Bytes(self.AppMethods.update_trip),
                 self.update_trip()],

                [Txn.application_args[0] == Bytes(self.AppMethods.participate_trip),
                 self.participate_trip()],

                [Txn.application_args[0] == Bytes(self.AppMethods.cancel_trip_participation),
                 self.cancel_participation()],

                [Txn.application_args[0] == Bytes(self.AppMethods.start_trip),
                 self.start_trip()]
            )
        )

        no_participants = App.globalGet(self.Variables.trip_capacity) == App.globalGet(
            self.Variables.max_capacity)
        trip_started = App.globalGet(self.Variables.app_state) == self.AppState.finished

        can_update = And(
            is_creator,
            no_participants,
            Not(trip_started)
        )

        can_delete = And(
            is_creator,
            Or(no_participants, trip_started)
        )

        actions = Cond(
            [Txn.application_id() == Int(0), self.app_create()],
            [Txn.on_completion() == OnComplete.OptIn, self.opt_in()],
            [Txn.on_completion() == OnComplete.NoOp, handle_noop],
            [Txn.on_completion() == OnComplete.UpdateApplication, Return(can_update)],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(can_delete)],

        )

        return actions

    def app_create(self):
        """
        CreateAppTxn
        Set the global_state of the app with given params
        Perform some checks for params validity
        :return:
        """
        valid_number_of_args = Txn.application_args.length() == Int(9)

        return Seq([
            Assert(valid_number_of_args),
            App.globalPut(self.Variables.creator_address, Txn.sender()),
            App.globalPut(self.Variables.creator_name, Txn.application_args[0]),
            App.globalPut(self.Variables.departure_address, Txn.application_args[1]),
            App.globalPut(self.Variables.arrival_address, Txn.application_args[2]),
            App.globalPut(self.Variables.departure_date, Txn.application_args[3]),
            App.globalPut(self.Variables.departure_date_round, Btoi(Txn.application_args[4])),
            App.globalPut(self.Variables.arrival_date, Txn.application_args[5]),
            App.globalPut(self.Variables.arrival_date_round, Btoi(Txn.application_args[6])),
            App.globalPut(self.Variables.trip_unit_cost, Btoi(Txn.application_args[7])),
            App.globalPut(self.Variables.max_capacity, Btoi(Txn.application_args[8])),
            App.globalPut(self.Variables.trip_capacity, Btoi(Txn.application_args[8])),
            App.globalPut(self.Variables.app_state, self.AppState.not_initialized),
            Assert(Global.round() <= App.globalGet(self.Variables.departure_date_round)),  # check dates are valid
            Assert(
                App.globalGet(self.Variables.departure_date_round) < App.globalGet(self.Variables.arrival_date_round)),
            Assert(App.globalGet(self.Variables.max_capacity) > Int(0)),  # at least a seat
            Return(Int(1))
        ])

    def update_trip(self):
        """
        UpdateAppTxn
        Update the global_state of the app with given params
        Perform some checks for params validity
        :return:
        """
        valid_number_of_args = Txn.application_args.length() == Int(10)
        no_participants = App.globalGet(self.Variables.trip_capacity) == App.globalGet(self.Variables.max_capacity)
        trip_ready = App.globalGet(self.Variables.app_state) == self.AppState.ready
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)

        can_update = And(
            no_participants,
            trip_ready,
        )

        return Seq([
            Assert(valid_number_of_args),
            Assert(is_creator),
            Assert(can_update),
            App.globalPut(self.Variables.creator_name, Txn.application_args[1]),
            App.globalPut(self.Variables.departure_address, Txn.application_args[2]),
            App.globalPut(self.Variables.arrival_address, Txn.application_args[3]),
            App.globalPut(self.Variables.departure_date, Txn.application_args[4]),
            App.globalPut(self.Variables.departure_date_round, Btoi(Txn.application_args[5])),
            App.globalPut(self.Variables.arrival_date, Txn.application_args[6]),
            App.globalPut(self.Variables.arrival_date_round, Btoi(Txn.application_args[7])),
            App.globalPut(self.Variables.trip_unit_cost, Btoi(Txn.application_args[8])),
            App.globalPut(self.Variables.max_capacity, Btoi(Txn.application_args[9])),
            App.globalPut(self.Variables.trip_capacity, Btoi(Txn.application_args[9])),
            Assert(Global.round() <= App.globalGet(self.Variables.departure_date_round)),  # check dates are valid
            Assert(
                App.globalGet(self.Variables.departure_date_round) < App.globalGet(self.Variables.arrival_date_round)),
            Assert(App.globalGet(self.Variables.max_capacity) > Int(0)),  # at least a seat
            Return(Int(1))
        ])

    def initialize_escrow(self, escrow_address):
        """
        NoOpTxn
        Initialize an escrow for this application
        :return:
        """
        curr_escrow_address = App.globalGetEx(Int(0), self.Variables.escrow_address)
        valid_number_of_transactions = Global.group_size() == Int(1)
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)
        trip_not_init = App.globalGet(self.Variables.app_state) == self.AppState.not_initialized

        update_state = Seq([
            App.globalPut(self.Variables.escrow_address, escrow_address),
            App.globalPut(self.Variables.app_state, self.AppState.initialized),
        ])

        return Seq([
            Assert(trip_not_init),
            curr_escrow_address,
            Assert(curr_escrow_address.hasValue() == Int(0)),
            Assert(valid_number_of_transactions),
            Assert(is_creator),
            update_state,
            Return(Int(1))
        ])

    def fund_escrow(self):
        """
        NoOpTxn
        Fund an escrow for this application
        :return:
        """
        valid_number_of_transactions = Global.group_size() == Int(2)
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)
        trip_init = App.globalGet(self.Variables.app_state) == self.AppState.initialized

        # check if the payment is valid
        valid_payment = And(
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].receiver() == App.globalGet(self.Variables.escrow_address),
            Gtxn[1].amount() == self.Constants.escrow_min_balance,
            Gtxn[1].sender() == Gtxn[0].sender(),
        )

        update_state = Seq([
            App.globalPut(self.Variables.app_state, self.AppState.ready),
        ])

        return Seq([
            Assert(trip_init),
            Assert(is_creator),
            Assert(valid_number_of_transactions),
            Assert(valid_payment),
            update_state,
            Return(Int(1))
        ])

    def opt_in(self):
        """
        OptInTxn
        Opt In a user to allow the usage of local_state
        :return:
        """
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)
        trip_ready = App.globalGet(self.Variables.app_state) == self.AppState.ready

        return Seq([
            Assert(trip_ready),
            Assert(Not(is_creator)),
            Assert(App.globalGet(self.Variables.app_state) == self.AppState.ready),
            Assert(Global.round() <= App.globalGet(self.Variables.departure_date_round)),
            Assert(App.globalGet(self.Variables.trip_capacity) > Int(0)),
            Return(Int(1))
        ])

    def participate_trip(self):
        """
        NoOpTxn
        A user want to participate the trip
        Perform validity checks and payment checks
        :return:
        """
        get_participant_state = App.localGetEx(Int(0), App.id(), self.Variables.book_capacity)
        trip_capacity = App.globalGet(self.Variables.trip_capacity)
        valid_number_of_transactions = Global.group_size() == Int(2)
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)
        book_capacity = Btoi(Txn.application_args[1])

        is_not_participating = Or(
            Not(get_participant_state.hasValue()),
            get_participant_state.value() == Int(0),
        )

        # check if user can participate
        can_participate = And(
            App.globalGet(self.Variables.app_state) == self.AppState.ready,
            Not(is_creator),
            App.globalGet(self.Variables.trip_capacity) >= book_capacity,  # check if there is an available seat
            Global.round() <= App.globalGet(self.Variables.departure_date_round),  # check if trip is started
            valid_number_of_transactions,
        )

        # check if the payment is valid
        valid_payment = And(
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].receiver() == App.globalGet(self.Variables.escrow_address),
            Gtxn[1].amount() == App.globalGet(self.Variables.trip_unit_cost)*book_capacity,
            Gtxn[1].sender() == Gtxn[0].sender(),
        )

        update_state = Seq([
            # check if user is not already participating
            get_participant_state,
            Assert(is_not_participating),
            # update state
            App.globalPut(self.Variables.trip_capacity, trip_capacity - book_capacity),  # decrease seats
            App.localPut(Int(0), self.Variables.book_capacity, book_capacity),  # set user as participating
        ])

        return Seq([
            Assert(can_participate),
            Assert(valid_payment),
            update_state,
            Return(Int(1))
        ])

    def cancel_participation(self):
        """
        NoOpTxn
        A user want to cancel trip participation
        Perform validity checks and payment-refund checks
        :return:
        """
        get_participant_state = App.localGetEx(Int(0), App.id(), self.Variables.book_capacity)
        trip_capacity = App.globalGet(self.Variables.trip_capacity)
        valid_number_of_transactions = Global.group_size() == Int(2)
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)
        
        is_participating = And(
            get_participant_state.hasValue(),
            get_participant_state.value() != Int(0),
        )

        # check if user can cancel participation
        can_cancel = And(
            App.globalGet(self.Variables.app_state) == self.AppState.ready,
            Not(is_creator),
            Global.round() <= App.globalGet(self.Variables.departure_date_round),  # check if trip is started
            valid_number_of_transactions,
        )

        valid_refund = And(
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].receiver() == Gtxn[0].sender(),
            Gtxn[1].amount() == App.globalGet(self.Variables.trip_unit_cost)*App.localGet(Int(0), self.Variables.book_capacity),
            Gtxn[1].sender() == App.globalGet(self.Variables.escrow_address),
        )

        update_state = Seq([
            # check if user is already participating
            get_participant_state,
            Assert(is_participating),
            # update state
            App.globalPut(self.Variables.trip_capacity, trip_capacity + App.localGet(Int(0), self.Variables.book_capacity)),  # increase seats
            App.localPut(Int(0), self.Variables.book_capacity, Int(0)),  # set user as not participating
            Return(Int(1))
        ])

        return Seq([
            Assert(can_cancel),
            Assert(valid_refund),
            update_state,
            Return(Int(1))
        ])

    def start_trip(self):
        """
        NoOpTxn
        The creator start the trip
        Perform validity checks and payment checks
        :return:
        """
        is_creator = Txn.sender() == App.globalGet(self.Variables.creator_address)
        valid_number_of_transactions = Global.group_size() == Int(2)

        can_start = And(
            App.globalGet(self.Variables.app_state) == self.AppState.ready,
            is_creator,  # creator only can perform this action
            Global.round() >= App.globalGet(self.Variables.departure_date_round),  # check if trip is started
            valid_number_of_transactions
        )

        valid_payment = And(
            Gtxn[1].type_enum() == TxnType.Payment,
            Gtxn[1].receiver() == App.globalGet(self.Variables.creator_address),
            Gtxn[1].sender() == App.globalGet(self.Variables.escrow_address),
        )

        update_state = Seq([
            App.globalPut(self.Variables.app_state, self.AppState.finished),
            Return(Int(1))
        ])

        return Seq([
            Assert(can_start),
            Assert(valid_payment),
            update_state,
            Return(Int(1))
        ])

    def approval_program(self):
        """
        approval_program of the contract
        :return:
        """
        return self.application_start()

    def clear_program(self):
        """
        clear_state_program of the contract
        :return:
        """
        trip_finished = App.globalGet(self.Variables.app_state) == self.AppState.finished

        return Seq(
            Assert(trip_finished),
            Return(Int(1))
        )

    @property
    def global_schema(self):
        """
        global_schema of the contract
        :return:
        """
        return algosdk.future.transaction.StateSchema(num_uints=6,
                                                      num_byte_slices=7)

    @property
    def local_schema(self):
        """
        local_schema of the contract
        :return:
        """
        return algosdk.future.transaction.StateSchema(num_uints=1,
                                                      num_byte_slices=0)
