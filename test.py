#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import os

from enum import Enum

from treelib import Tree


class TreeX(Tree):
    def perfect_merge(self, nid, new_tree, deep=False) -> None:
        if not (isinstance(new_tree, Tree) or isinstance(new_tree, TreeX)):
            raise Exception('The new tree to merge is not a valid tree.')

        if new_tree is None:
            return

        if new_tree.root is None:
            return

        if nid is None:
            if self.root is None:
                self.add_node(new_tree[new_tree.root])
            nid = self.root
        
        if not self.contains(nid):
            raise Exception('Node <{}> is not in the tree!'.format(nid))

        current_node = self[nid]

        if current_node.tag != new_tree[new_tree.root].tag:
            raise Exception('Current node not same with root of new tree.')

        childs = self.children(nid)
        child_tags = [child.tag for child in childs]
        new_childs = new_tree.children(new_tree.root)
        new_subtrees = [new_tree.subtree(child.identifier) for child in new_childs]

        if not childs:
            for new_subtree in new_subtrees:
                self.paste(nid=nid, new_tree=new_subtree, deep=deep)
        else:
            for new_child in new_childs:
                if new_child.tag not in child_tags:
                    self.paste(nid=nid, new_tree=new_tree.subtree(new_child.identifier), deep=deep)
                    continue
                self.perfect_merge(
                    childs[child_tags.index(new_child.tag)].identifier,
                    new_tree.subtree(new_child.identifier),
                    deep=deep,
                )



t = TreeX()
t.create_node('1', '1', parent=None)
t.create_node('2', '2', parent='1')
t.create_node('3', '3', parent='2')
t.create_node('4', '4', parent='3')
t.create_node('5', '5', parent='4')
t.create_node('6', '6', parent='5')
t.show()