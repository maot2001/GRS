import copy

class Node:
    def __init__(self, rep, value, father):
        self.value = value
        self.children = []
        self.count = 1
        self.max = {}
        self.repetitions = rep
        
        if father is None:
            self.road = []
        else:
            self.road = father.road.copy()
            self.road.append(value)

class Bayesian_Network(Node):
    def __init__(self, rep):
        super().__init__(rep, None, None)
        self.change_act_int = {}
        self.change_int_act = {}
        self.repetitions = rep
        self.markers = [self]

    def copy(self):
        return copy.deepcopy(self)

    def insert(self, vector):
        if not vector in self.change_act_int:
            self.change_int_act[len(self.change_act_int)] = vector
            self.change_act_int[vector] = len(self.change_act_int)

        id_act = self.change_act_int[vector]

        for i in range(len(self.markers)-1, -1, -1):
            node = None
            m = self.markers[i]

            for n in m.children:
                if n.value == id_act:
                    node = n
                    break

            if node is None:
                new_node = Node(self.repetitions, id_act, m)
                m.children.append(new_node)
                if not vector[1:] in m.max:
                    m.max[vector[1:]] = new_node
                if hasattr(m, 'markers'):
                    m.markers.append(new_node)
                    if len(m.children) > 1:
                        m.count += 1
                else:
                    self.markers[i] = new_node

            else:
                node.count += 1
                if m.max[vector[1:]].count < node.count:
                    m.max[vector[1:]] = node

                if hasattr(m, 'markers'):
                    m.markers.append(node)
                    m.count += 1
                else:
                    self.markers[i] = node

            if (len(self.markers[i].road) - len(set(self.markers[i].road))) >= self.repetitions:
                self.markers.pop(i)

    def predict(self, vector):
        action = None
        value = 0

        for m in self.markers:
            if (vector) in m.max and value <= (m.max[(vector)].count / m.count):
                value = (m.max[(vector)].count / m.count)
                action = self.change_int_act[m.max[(vector)].value][0]

        return action
