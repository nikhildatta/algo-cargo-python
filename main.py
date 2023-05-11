import random

from algosdk import account
from algosdk.v2client import algod
from numpy.core.defchararray import strip

from constants import Constants, get_env
from helpers import algo_helper
from models.Delivery import Delivery
from utilities import utils


def read_state(algod_client, app_id, user_private_key=None, show_debug=False):
    """
    Get the dApp global state / local state
    :param algod_client:
    :param app_id:
    :param user_private_key:
    :param show_debug:
    """

    if app_id is None:
        utils.console_log("Invalid app_id")
        return False

    local_state = None
    if user_private_key is not None:
        # read local state of application
        local_state = algo_helper.read_local_state(algod_client,
                                                   account.address_from_private_key(user_private_key),
                                                   app_id),

    # read global state of application
    global_state, creator, approval_program, clear_state_program = algo_helper.read_global_state(client=algod_client,
                                                                                                 app_id=app_id,
                                                                                                 to_array=False,
                                                                                                 show=False)
    escrow_address = algo_helper.BytesToAddress(global_state.get('escrow_address'))

    utils.console_log("App id: {}".format(app_id), 'blue')
    utils.console_log("Global State:", 'blue')
    print(utils.toArray(global_state))
    if local_state is not None:
        utils.console_log("Local State:", 'blue')
        print(utils.toArray(local_state))
    utils.console_log("Approval Program:", 'blue')
    print(approval_program)
    utils.console_log("Clear State Program:", 'blue')
    print(clear_state_program)
    utils.console_log("Creator Address:", 'blue')
    print(creator)
    utils.console_log("Escrow Address:", 'blue')
    print(escrow_address)
    utils.console_log("Escrow Info:", 'blue')
    print(algod_client.account_info(escrow_address))

    if show_debug:
        utils.console_log("Application Info:", 'blue')
        app_info = algod_client.application_info(app_id)
        utils.parse_response(app_info)


def get_test_user(user_list, ask_selection=True):
    """
    Select a test user account from given user list
    :param user_list:
    :param ask_selection: if True, ask user for selection, otherwise select the user randomly
    """
    if ask_selection:
        print('With which user?')
        for i in range(0, len(user_list)):
            print('{}) {}'.format(i, user_list[i].get('name')))
        y = int(strip(input()))
        if y <= 0 or y > len(user_list):
            y = 0
    else:
        y = random.randint(0, len(user_list) - 1)

    return user_list[y]


def main():
    algod_client = algod.AlgodClient(Constants.algod_token, Constants.algod_address)
    app_id = int(get_env('APP_ID'))
    accounts = Constants.accounts

    logistic_manager = Delivery(algod_client=algod_client, app_id=app_id)
    color = 'blue'
    
    while True:
        utils.console_log("--------------------------------------------", color)
        utils.console_log('What do you want to do?', color)
        utils.console_log('1) Create Delivery', color)
        utils.console_log('2) Participate', color)
        utils.console_log('3) Cancel Participation', color)
        utils.console_log('4) Start Delivery', color)
        utils.console_log('5) Update Delivery', color)
        utils.console_log('6) Delete Delivery', color)
        utils.console_log('7) Finish Delivery', color)
        utils.console_log('8) Get Delivery State', color)
        utils.console_log("--------------------------------------------", color)
        x = int(strip(input()))
        if x == 1:
            # ------- delivery info ---------
            creator = get_test_user(accounts, True)
            creator_private_key = algo_helper.get_private_key_from_mnemonic(creator.get('mnemonic'))
            delivery_creator_name = creator.get('name')
            #delivery_start_add = input("Enter Dispatch Point: ")
            delivery_start_add = "Chennai"
            #delivery_end_add = input("Enter Destination: ")
            delivery_end_add = "Mumbai"
            delivery_start_date = input("Enter Dispatch Time (yyyy-mm-dd hh:mm): ")
            delivery_end_date = input("Enter Destination Time (yyyy-mm-dd hh:mm): ")
            #delivery_unit_cost = int(input("Enter Transportation Cost per kg: "))
            delivery_unit_cost = 10
            #delivery_capacity = int(input("Enter Total Capacity in kg: "))
            delivery_capacity = 1000
            # ---------------------------
            logistic_manager.create_app(creator_private_key=creator_private_key,
                                       delivery_creator_name=delivery_creator_name,
                                       delivery_start_address=delivery_start_add,
                                       delivery_end_address=delivery_end_add,
                                       delivery_start_date=delivery_start_date,
                                       delivery_end_date=delivery_end_date,
                                       delivery_unit_cost=delivery_unit_cost,
                                       delivery_capacity=delivery_capacity)
            logistic_manager.initialize_escrow(creator_private_key)
            logistic_manager.fund_escrow(creator_private_key)
        elif x == 2:
            if logistic_manager.app_id is None:
                utils.console_log("Invalid app_id")
                continue
            book_user = get_test_user(accounts, True)
            book_user_pk = algo_helper.get_private_key_from_mnemonic(book_user.get('mnemonic'))
            #book_capacity = int(input("Enter Needed Capacity in kg: "))
            book_capacity = 20
            logistic_manager.participate(book_user_pk, book_user.get('name'), book_capacity)
        elif x == 3:
            if logistic_manager.app_id is None:
                utils.console_log("Invalid app_id")
                continue
            book_user = get_test_user(accounts, True)
            book_user_pk = algo_helper.get_private_key_from_mnemonic(book_user.get('mnemonic'))
            logistic_manager.cancel_participation(book_user_pk, book_user.get('name'))
        elif x == 4:
            if logistic_manager.app_id is None:
                utils.console_log("Invalid app_id")
                continue
            creator = get_test_user(accounts, True)
            creator_private_key = algo_helper.get_private_key_from_mnemonic(creator.get('mnemonic'))
            delivery_creator_name = creator.get('name')
            logistic_manager.start_delivery(creator_private_key)
        elif x == 5:
            if logistic_manager.app_id is None:
                utils.console_log("Invalid app_id")
                continue
            # ------- delivery info ---------
            creator = get_test_user(accounts, True)
            creator_private_key = algo_helper.get_private_key_from_mnemonic(creator.get('mnemonic'))
            delivery_creator_name = creator.get('name')
            update_option = int(input("What would you like to update?\n\
                    1) Dispatch Details\n\
                    2) Destination Details\n\
                    3) Transportation Details\n"))
            if update_option == 1:
                delivery_start_add = input("Enter Dispatch Point: ")
                delivery_start_date = input("Enter Dispatch Time (yyyy-mm-dd hh:mm): ")
            elif update_option == 2:
                delivery_end_add = input("Enter Destination: ")
                delivery_end_date = input("Enter Destination Time (yyyy-mm-dd hh:mm): ")
            elif update_option == 3:
                delivery_unit_cost = int(input("Enter Transportation Cost per kg: "))
                delivery_capacity = int(input("Enter Total Capacity in kg: "))
            # ---------------------------
            if update_option in [1,2,3]:
                logistic_manager.update_delivery_info(creator_private_key=creator_private_key,
                                             delivery_creator_name=delivery_creator_name,
                                             delivery_start_address=delivery_start_add,
                                             delivery_end_address=delivery_end_add,
                                             delivery_start_date=delivery_start_date,
                                             delivery_end_date=delivery_end_date,
                                             delivery_unit_cost=delivery_unit_cost,
                                             delivery_capacity=delivery_capacity)
        elif x == 6:
            utils.console_log("Are you sure?", 'red')
            y = strip(input())
            if y != "y" and y != "yes":
                continue
            if logistic_manager.app_id is None:
                utils.console_log("Invalid app_id")
            creator = get_test_user(accounts, True)
            creator_private_key = algo_helper.get_private_key_from_mnemonic(creator.get('mnemonic'))
            delivery_creator_name = creator.get('name')
            logistic_manager.close_delivery(creator_private_key, accounts)
        elif x == 7:
            if logistic_manager.app_id is None:
                utils.console_log("Invalid app_id")
                continue
            creator = get_test_user(accounts, True)
            creator_private_key = algo_helper.get_private_key_from_mnemonic(creator.get('mnemonic'))
            delivery_creator_name = creator.get('name')
            logistic_manager.finish_delivery(creator_private_key)
        elif x == 8:
            read_state(algod_client, logistic_manager.app_id, show_debug=False)
        else:
            print("Exiting..")
            break


if __name__ == "__main__":
    main()
