from enum import StrEnum


class RewriteActionEnum(StrEnum):
    NOOP = "noop"
    REMOVE_INVERSE_PAIR = "remove_inverse_pair"
    MERGE_ROTATIONS = "merge_rotations"
