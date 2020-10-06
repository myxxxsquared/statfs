import os
import csv
import stat
import sys
import collections

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QApplication
from PyQt5.QtGui import QFont, QFontDatabase


class TreeNode:
    pass


def to_tree(input_file_name):
    reader = iter(csv.reader(open(input_file_name)))
    tree_nodes = {}

    (fname, st_mode, _, _, _, _, _, st_size, _, _, _,) = next(reader)
    st_mode = int(st_mode)
    st_size = int(st_size)

    node = TreeNode()
    fname = fname.rstrip("/") or fname
    node.name = fname
    node.size = st_size
    node.parent = None
    node.children = []
    node.ext = None
    if stat.S_ISDIR(st_mode):
        tree_nodes[fname] = node

    root_node = node

    for (fname, st_mode, _, _, _, _, _, st_size, _, _, _,) in reader:
        st_mode = int(st_mode)
        st_size = int(st_size)
        folder_name, file_name = os.path.split(fname)
        node = TreeNode()
        node.name = file_name
        node.size = st_size
        parent = tree_nodes[folder_name]
        node.parent = parent
        node.children = []
        node.ext = None
        parent.children.append(node)
        if stat.S_ISDIR(st_mode):
            tree_nodes[fname] = node
        while parent is not None:
            parent.size += st_size
            parent = parent.parent

    return root_node


def to_human_str(size):
    if size < 1024:
        return f"{size: 4d}    "
    if size < 1024 * 1024:
        return f"{size/1024: 7.02f}K"
    if size < 1024 * 1024 * 1024:
        return f"{size/1024/1024: 7.02f}M"
    if size < 1024 * 1024 * 1024 * 1024:
        return f"{size/1024/1024/1024: 7.02f}G"
    return f"{size/1024/1024/1024/1024: 7.02f}T"


def main():
    root_node = to_tree("result.csv")

    def sort_children(n):
        n.children = sorted(n.children, key=lambda x: x.size, reverse=True)
        for x in n.children:
            sort_children(x)

    sort_children(root_node)

    app = QApplication([])
    font = QFontDatabase.systemFont(QFontDatabase.FixedFont)

    root_item = QTreeWidgetItem([to_human_str(root_node.size), root_node.name])
    root_item.setFont(12, font)

    def add_children(q_parent, n_parent):
        for n in n_parent.children:
            node = QTreeWidgetItem([to_human_str(n.size), n.name])
            node.setFont(12, font)
            q_parent.addChild(node)
            add_children(node, n)

    add_children(root_item, root_node)
    widget = QTreeWidget()
    widget.setFont(font)
    widget.setHeaderLabels(["Size", "Name"])
    widget.addTopLevelItem(root_item)
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
