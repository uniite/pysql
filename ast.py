

class Tree (object):
    """ An abstract syntax tree. """

    # TODO: Implement the depth index
    # TODO: Make unit tests for this

    def __init__ (self):
        self.root = None
        self.last = None
        self.depth_index = []


    def add_op (self, item):
        """ Adds an operation to the tree. """

        op_type, op_value, op_precedence = item

        # If this is the first node, just add it the simple way
        self.add_node(Node(item))

        # Take into account the operator's precedence.
        # High precedence means it needs to be executed first,
        # which corresponds to being lower on the tree.
        t, v, p = self.last.data
        next = None
        if p > op_precedence:
            prev = self.last
            # Try further up
            while True:
                next = prev.parent
                # We've reached the top; can't go any further
                if not next:
                    break
                # Check the precedence against another node
                t, v, p = next.data
                if p > op_precedence:
                    prev = next
                # We've found where the op needs to be inserted
                else:
                    break
        else:
            next = self.last

        # Now that we know the first node to have lower or equal precedence,
        # we know where node should go (right above it).
        # TODO: See how > vs >= affects the order (esp for left-to-right ops).
        node.left = next
        node.parent = next.parent
        next.parent = node
        node.refresh_depth()




    def add_value (self, item):
        """
        Adds a value (or identifier) to the tree.
        """

        # Since values have no precedence,
        # they always get added to the end.
        add_node(Node(item))


    def add_node (self, node):
        # Set this node as the root node if we don't have one
        # (and consequently, it becomes the last and only node)
        if not self.root:
            self.root = node
            self.last = node

        # Handle the special cast where we only have one node
        if self.root == self.last:
            # We know right away where to put the new node
            self.root.left = node
            node.parent = self.root

        # This node now becomes the last one
        # TODO: Is this problematic with unary and other obscure operators?
        if not self.last.parent.right:
            self.last.parent.right = node
            node.parent = self.last.parent
        else:
            self.last.left = node
            node.parent = self.last

        # Now, set the node's depth
        node.refresh_depth()
        # Also, this node is last now
        self.last = node





class Node (object):
    """ A single node in an abstract syntax tree. """

    def __init__ (self, data, left=None, right=None, parent=None):
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent

    def refresh_depth (self):
        if node.parent:
            node.depth = parent.depth + 1
        else:
            node.depth = 0

  