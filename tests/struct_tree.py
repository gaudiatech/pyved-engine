import pyved_engine as pyv

TreeNode = pyv.struct.TreeNode


x = TreeNode('salut xy', None)
my_tree = x.tree_ref
y = TreeNode(88, x)
z = TreeNode(15, y)

print(' should print:\n0 1 2')
print(x.depth, y.depth, z.depth)

print(' should print:\nFalse False True False 1 0')
print(y.is_root(), x.is_leaf(), z.is_leaf(), y.is_leaf(), y.child_count, z.child_count)

print(' should print:\n2 2 5')
kappa = TreeNode(128, y)
ultima = kappa.tree_ref.append_value(129, kappa)
print(kappa.depth, y.child_count, my_tree.count)

print(' should print:\nsalut xy')
print(my_tree.root.value)

print(' should print:\n-same object ref twice-')
print(my_tree.node_by_content(129), ultima)

print(' should print:\nNone')
print(my_tree.node_by_content('lol'))

print('*****************')
print('*****************')
print(my_tree)
