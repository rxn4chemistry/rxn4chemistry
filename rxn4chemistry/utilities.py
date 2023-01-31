import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def check_starting_material_availability(tree: dict) -> bool:
    """
    Check all tree node leafs for material availability (intended as commercially available).

    Args:
        tree (dict): Retrosynthesis tree.

    Returns:
        bool: return True if all node leafs are commercially available.
    """

    commercially_available = True
    children = tree.get("children", [])
    # node is a leaf
    if len(children) == 0:
        try:
            commercially_available = tree["isCommercial"]
        except KeyError:
            logger.warning("No information on commercial availability")
            commercially_available = False
    else:
        # process children recursively
        for child in tree["children"]:
            if not check_starting_material_availability(child):
                commercially_available = False
    return commercially_available


def check_results_for_material_availability(results: dict) -> List[Dict[str, Any]]:
    """
    Check all trees in results for material availability in all node leafs (intended as commercially available).

    Args:
        results (dict): Contains retrosynthetic_paths with all retrosynthesis trees that make the path.

    Returns:
        dict: returns a dict with the sequence ids as keys and commercially availability in all tree nodes as value.
    """
    return [
        {
            "index": index,
            "sequence_id": tree["sequenceId"],
            "are_materials_available": check_starting_material_availability(tree),
        }
        for index, tree in enumerate(results["retrosynthetic_paths"])
    ]
