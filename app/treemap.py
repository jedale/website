# support stuff to build treemaps of NFL team cap usage
import squarify
import pandas as pd

class Node:
    
    def __init__(self, label, data):
        self.label = label
        self.data = data
        self.children = None

# tree structure for a single NFL Team
NFLTeam = Node('Team',0)
NFLTeam.children = [Node('Offense', 0),
                    Node('Defense', 0),
                    Node('SpecialTeams', 0)]
NFLTeam.children[0].children = [Node('QB', 0),
                                Node('RB', 0),
                                Node('OL', 0),
                                Node('TE', 0),
                                Node('WR', 0)]
NFLTeam.children[1].children = [Node('DL', 0),
                                Node('LB', 0),
                                Node('DB', 0)]
NFLTeam.children[2].children = [Node('K', 0),
                                Node('P', 0),
                                Node('LS', 0)]
NFLTeam.children[0].children[1].children = [Node('FB', 0),
                                            Node('HB', 0)]
NFLTeam.children[0].children[2].children = [Node('T', 0),
                                            Node('G', 0),
                                            Node('C', 0),
                                            Node('LT', 0)]
NFLTeam.children[1].children[0].children = [Node('NT', 0),
                                            Node('DT', 0),
                                            Node('DE', 0)]
NFLTeam.children[1].children[1].children = [Node('OLB', 0),
                                            Node('ILB', 0),
                                            Node('MLB', 0)]
NFLTeam.children[1].children[2].children = [Node('CB', 0),
                                            Node('S', 0),
                                            Node('FS', 0),
                                            Node('SS', 0)]

colors = {
    'Offense' : '#78BE20',
    'QB' : '#78BE20',
    'TE' : '#78BE20',
    'G' : '#78BE20',
    'LT' : '#78BE20',
    'WR' : '#78BE20',
    'RB' : '#78BE20',
    'C' : '#78BE20',
    'OL': '#78BE20',
    'RT' : '#78BE20',
    'T' : '#78BE20',
    'FB' : '#78BE20',
    'Defense' : '#0C2340',
    'DE' : '#0C2340',
    'FS' : '#0C2340',
    'DT' : '#0C2340',
    'ILB' : '#0C2340',
    'OLB' : '#0C2340',
    'CB' : '#0C2340',
    'SS' : '#0C2340',
    'S' : '#0C2340',
    'LB' : '#0C2340',
    'DB' : '#0C2340',
    'DL' : '#0C2340',
    'SpecialTeams' : '#A2AAAD',
    'P' : '#A2AAAD',
    'K' : '#A2AAAD',
    'LS' : '#A2AAAD'
}


# uses squarify to generate a list of rectangles for the treemap
def treemap(queue, glyphs):
    if len(queue) == 0:
        return
        
    node = queue[0]
    queue.pop(0)
        
    if node.children:
        # squarify the children based on parent coordinates
        values = list()
        [values.append(child.data) for child in node.children]
        values = squarify.normalize_sizes(values, node.dx, node.dy)
        rects = squarify.padded_squarify(values, 
                                  node.x, node.y, 
                                  node.dx, node.dy)
        
        # have to save glyph info so we can squarify children
        for i in range(len(node.children)):
            node.children[i].x = rects[i]['x']
            node.children[i].y = rects[i]['y']
            node.children[i].dx = rects[i]['dx']
            node.children[i].dy = rects[i]['dy']
            rects[i]['label'] = node.children[i].label
              
        [queue.append(child) for child in node.children]
        [glyphs.append(rect) for rect in rects]
        
    treemap(queue, glyphs)

# populate the tree via a reverse order traversal
def filltree(node, data):    
    if node.children:
        total = 0
        for child in node.children:
            filltree(child, data)
            total = total + child.data
        node.data = total + data[data.Position == node.label].Cap_Hit.sum()
    else:
        # node doesn't have children; just populate it based on label
        node.data = data[data.Position == node.label].Cap_Hit.sum()

def preptree(node):
    if node.children:
        for child in node.children:
            preptree(child)
        # remove nodes that have zero value
        node.children = [x for x in node.children if x.data != 0]
        node.children.sort(key=lambda x: x.data, reverse=True)
    