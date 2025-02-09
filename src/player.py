from random import randint, random, choice, choices
from bay_net import Bayesian_Network

options = ['like', 'unlike', 'save', 'comment', 'forward', 'scroll', 'follow', 'wait', 'publish', 'include_group']

class MoveSets:
    def __init__(self, sequency, probability):
        self.sequency = sequency
        self.probability = probability
        self.moves = []
        self.actual = 0

    def get_move(self, content, collab):
        if len(self.moves) == 0:
            moves = self.sequency(content, collab)

            if moves is None:
                return 'wait'

            self.moves = moves

        move = self.moves[self.actual]
        
        self.actual += 1
        if self.actual == len(self.moves):
            self.moves.clear()
            self.actual = 0

        return move
    
def randomize(content, collab):
    return [choice(options)]
    
def fast_like(content, collab):
    if random() < content or random() < collab:
        return ['like', 'scroll']
    
def slow_like(content, collab):
    if random() < content or random() < collab:
        opt = choice(['comment', 'save', 'forward'])
        return ['like', opt, 'scroll']

def seq_scroll(content, collab):
    count = randint(1, 5)
    return ['scroll'] * count

def really_slow_like(content, collab):
    if random() < content or random() < collab:
        count = randint(1, 5)
        opt = choices(['comment', 'save', 'forward', 'follow'], k=count)
        opt.insert(randint(0, count-1), 'like')
        opt.append('scroll')
        return opt
    
def fast_unlike(content, collab):
    if random() < content or random() < collab:
        return ['unlike', 'scroll']
    
def slow_unlike(content, collab):
    if random() < content or random() < collab:
        opt = choice(['comment', 'save', 'forward'])
        return ['unlike', opt, 'scroll']
    
def really_slow_unlike(content, collab):
    if random() < content or random() < collab:
        count = randint(1, 3)
        opt = choices(['comment', 'forward'], k=count)
        opt.insert(randint(0, count-1), 'unlike')
        opt.append('scroll')
        return opt
    
def publish(content, collab):
    return ['publish']

def include_group(content, collab):
    return ['include_group']

class Player:
    def __init__(self, moves = [fast_like, fast_unlike, seq_scroll, slow_like, slow_unlike, randomize, really_slow_like, 
                                really_slow_unlike, publish, include_group]):
        probs = {}
        for i in range(len(moves)-1):
            probs[moves[i]] = random()
        probs[moves[-1]] = 1
        probs = dict(sorted(probs.items(), key=lambda item: item[1]))
        
        self.movesets = []
        for p in probs:
            self.movesets.append(MoveSets(p, probs[p]))

        self.last = 'wait'

    def do_act(self, content, collab):
        if self.last == 'wait' or len(self.move.moves) == 0:
            val = random()
            for m in self.movesets:
                if val < m.probability:
                    self.move = m
                    break

        self.last = self.move.get_move(content, collab)
        return self.last
    