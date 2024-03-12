import hc_constants

def is_mork(user_id:int):
    """Is the id passed in the id of a MORK"""
    return user_id == hc_constants.MORK or user_id == hc_constants.MORK_2
