import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def check_starting_material_availability(tree: dict):
    """
    Check all tree node leafs for material availability. (Commercially available)

    Args:
        tree (dict): Retrosynthesis tree.

    Returns:
        bool: return True if all node leafs are commercially available.
    """

    children = tree.get("children", [])
    # node is a leaf
    if len(children) == 0:
        try:
            commercially_available = tree["isCommercial"]
            return commercially_available
        except KeyError:
            logger.warning("No information on commercial availability")
            return False
    else:
        # process children recursively
        for child in tree["children"]:
            if not check_starting_material_availability(child):
                return False
    return tree


def check_results_for_material_availability(results: dict):
    """
    Check all trees in results for material availability in all node leafs. (Commercially available)

    Args:
        results (dict): Contains retrosynthetic_paths with all retrosynthesis trees that make the path.

    Returns:
        dict: returns a dict with the sequence ids as keys and commercially availability in all tree nodes as value.
    """
    return [
        {
            tree[index]["sequenceId"]: check_starting_material_availability(tree)
            for index, tree in enumerate(results["retrosynthetic_paths"])
        }
    ]
