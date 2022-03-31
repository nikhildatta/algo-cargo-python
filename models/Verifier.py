from pyteal import compileTeal, Mode

from helpers import algo_helper
from models.ApplicationManager import ApplicationManager
from smart_contracts.contract_verifier import VerifierContract
from utilities import utils


class Verifier:
    def __init__(self, algod_client, app_id=None):
        self.algod_client = algod_client
        self.teal_version = 5
        self.app_contract = VerifierContract()
        self.app_id = app_id

    def create_verifier(self,
                        creator_private_key: str,
                        approval_program_hash: str,
                        clear_state_program_hash: str):
        """
        Create the Smart Contract dApp and start the trip
        :param creator_private_key:
        :param approval_program_hash:
        :param clear_state_program_hash:
        :return:
        """
        # compile program to TEAL assembly
        approval_program_compiled = compileTeal(
            self.app_contract.approval_program(),
            mode=Mode.Application,
            version=self.teal_version,
        )

        clear_program_compiled = compileTeal(
            self.app_contract.clear_program(),
            mode=Mode.Application,
            version=self.teal_version
        )

        # compile program to binary
        approval_program_compiled = algo_helper.compile_program(self.algod_client, approval_program_compiled)
        clear_state_program_compiled = algo_helper.compile_program(self.algod_client, clear_program_compiled)

        app_args = [
            approval_program_hash,
            clear_state_program_hash,
        ]

        try:
            txn = ApplicationManager.create_app(self.algod_client,
                                                creator_private_key,
                                                approval_program_compiled,
                                                clear_state_program_compiled,
                                                self.app_contract.global_schema,
                                                self.app_contract.local_schema,
                                                app_args)

            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            self.app_id = txn_response['application-index']
            utils.console_log("Application Created. New app-id: {}".format(self.app_id), "green")
        except Exception as e:
            utils.console_log("Error during create_app call: {}".format(e))
            return False

        return self.app_id

    def update_verifier(self,
                        creator_private_key: str,
                        approval_program_hash: str,
                        clear_state_program_hash: str):
        """
        Update the verifier
        :param creator_private_key:
        :param approval_program_hash:
        :param clear_state_program_hash:
        :return:
        """
        # compile program to TEAL assembly
        approval_program_compiled = compileTeal(
            self.app_contract.approval_program(),
            mode=Mode.Application,
            version=self.teal_version,
        )

        clear_program_compiled = compileTeal(
            self.app_contract.clear_program(),
            mode=Mode.Application,
            version=self.teal_version
        )

        # compile program to binary
        approval_program_compiled = algo_helper.compile_program(self.algod_client, approval_program_compiled)
        clear_state_program_compiled = algo_helper.compile_program(self.algod_client, clear_program_compiled)

        app_args = [
            approval_program_hash,
            clear_state_program_hash,
        ]

        try:
            txn = ApplicationManager.update_app(self.algod_client,
                                                creator_private_key,
                                                approval_program_compiled,
                                                clear_state_program_compiled,
                                                self.app_contract.global_schema,
                                                self.app_contract.local_schema,
                                                app_args)

            ApplicationManager.send_transaction(self.algod_client, txn)
            utils.console_log("Verifier updated.", "green")
        except Exception as e:
            utils.console_log("Error during update call: {}".format(e))
            return False

    def delete_verifier(self, creator_private_key: str):
        """
        Delete the Smart Contract dApp
        :param creator_private_key:
        :return:
        """

        try:
            # delete application
            txn = ApplicationManager.delete_app(self.algod_client, creator_private_key, self.app_id)
            txn_response = ApplicationManager.send_transaction(self.algod_client, txn)
            utils.console_log("Deleted Application with app-id: {}".format(txn_response["txn"]["txn"]["apid"]), "green")
        except Exception as e:
            utils.console_log("Error during delete_app call: {}".format(e))
            return False
