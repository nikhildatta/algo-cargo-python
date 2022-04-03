from pyteal import *


def contract_escrow(app_id: int):
    """
    Stateless contract to perform payments for a contract
    :param app_id:
    :return:
    """
    return Seq([
        Assert(Global.group_size() == Int(2)),
        Assert(Gtxn[0].application_id() == Int(app_id)),

        Assert(Gtxn[1].type_enum() == TxnType.Payment),

        Return(Int(1))
    ])
