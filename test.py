#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import uuid

from enum import Enum, unique

from treelib import Tree

import sys

import os


os.symlink('./jay.txt', './jay.txt.link')

print(os.path.islink('./jay.txt.link'))

sys.exit(1)

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


trees = [
    '1/2/3/4/5/6|1/2/3/4/5/9',
    '1/2/3/8/9',
    '1/2/3/5/7',
    '1/2',
    '1/2/3/5/9',
]

class self():
    @unique
    class AudiosTreeNodeType(Enum):
        ROOT = 'root'
        FOLDER = 'folder'
        PLAYLIST = 'playlist'
        TRACK = 'track'

    AUDIOS_TREE_ROOT_TAG = '--root-tag--'
    AUDIOS_TREE_ROOT_NID = '--root-nid--'

    @staticmethod
    def generate_persistent_id() -> str:
        return str(uuid.uuid4()).replace('-', '')[:16].upper()

    audios_tree = None

self.audios_tree = TreeX()
self.audios_tree.create_node(self.AUDIOS_TREE_ROOT_TAG, self.AUDIOS_TREE_ROOT_NID)
audio = 'COMMON-TAG'
track_id = track_persistent_id = audio_object = None

for grouping in trees:
    for group in grouping.split('|'):
        group = re.sub(r'\/+', r'/', group).rstrip('/')
        if not group:
            continue
        tags = list(filter(lambda x: x, group.split('/')))
        if not tags:
            continue
        tags = [self.AUDIOS_TREE_ROOT_TAG] + tags
        subtree = TreeX()
        last_nid = self.AUDIOS_TREE_ROOT_NID
        for i in range(len(tags)):
            tag, nid = tags[i], self.generate_persistent_id()
            parent = None if i == 0 else last_nid
            node_type = self.AudiosTreeNodeType.FOLDER
            if i == 0:
                node_type = self.AudiosTreeNodeType.ROOT
                nid = self.AUDIOS_TREE_ROOT_NID
            elif i == len(tags) - 1:
                node_type = self.AudiosTreeNodeType.PLAYLIST
            subtree.create_node(
                tag, nid, parent=parent,
                data=[node_type, -1, nid, parent],
            )
            last_nid = nid
        subtree.create_node(
            audio,
            self.generate_persistent_id(),
            parent=last_nid,
            data=[self.AudiosTreeNodeType.TRACK, track_id, track_persistent_id, audio_object],
        )
        self.audios_tree.perfect_merge(self.AUDIOS_TREE_ROOT_NID, subtree, deep=False)

self.audios_tree.show()