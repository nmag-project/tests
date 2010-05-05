import math

def vec_add(a, b): return [ai + bi for ai, bi in zip(a, b)]
def vec_sub(a, b): return [ai - bi for ai, bi in zip(a, b)]
def vec_scal(a, b): return sum([ai*bi for ai, bi in zip(a, b)])
def vec_mul(a, x): return [ai*x for ai in a]
def vec_norm2(a): return vec_scal(a, a)
def vec_norm(a): return math.sqrt(vec_scal(a, a))
def vec_unit(a): return vec_mul(a, 1.0/vec_norm(a))

def vec_ortho(va, vb):
    """Returns a vector obtained by rotating a in the plane a-b by 90 degrees
    towards the vector b."""
    a2 = vec_norm2(va)
    a = math.sqrt(a2)
    nb = vec_sub(vb, vec_mul(va, vec_scal(va, vb)/a2))
    return vec_mul(nb, a/vec_norm(nb))

def sample(fn, end, start=0.0, framerate=25):
    t = start
    dt = 1.0/framerate
    while t < end:
        fn(t)
        t += dt

class PathPiece:
    def __init__(self, fn, start=0.0, end=1.0, duration=1.0):
        self.fn = fn
        self.start = start
        self.end = end
        self.duration = duration

class Path:
    def __init__(self, t0=0.0):
        self.path_pieces = []
        self.t0s = None
        self.t0 = 0.0
        self.last_piece_accessed = None
        self.last_point = None

    def add_path(self, fn, start=0.0, end=1.0, duration=1.0):
        pp = PathPiece(fn, start=start, end=end, duration=duration)
        self.path_pieces.append(pp)
        self.t0s = None

    def _get_t0s(self):
        if self.t0s != None:
            return self.t0s

        t = self.t0
        t0s = [self.t0]
        for pp in self.path_pieces:
            t += pp.duration
            t0s.append(t)

        self.t0s = t0s
        return t0s

    def get_max_time(self):
        t0s = self._get_t0s()
        return t0s[-1]

    def _get_from_to(self, from_point, to_point):
        if from_point == None:
            if self.last_point != None:
                from_point = self.last_point

        self.last_point = to_point
        return (from_point, to_point)

    def add_segment(self, from_point=None, to_point=None, duration=1.0):
        if from_point == None:
            if self.last_point != None:
                from_point = self.last_point

            else:
                self.last_point = to_point
                return

        self.last_point = to_point

        def line(t):
            return [ai + t*float(bi - ai)
                    for ai, bi in zip(from_point, to_point)]

        self.add_path(line, start=0.0, end=1.0, duration=duration)

    def add_segments(self, points, durations=None):
        l = len(points)
        for i in range(l - 1):
            d = 1.0
            if i < len(durations):
                d = durations[i]
            self.add_segment(points[i], points[i+1], duration=d)

    def add_arc(self, center, to_point, from_point=None, duration=1.0):
        from_point, to_point = self._get_from_to(from_point, to_point)
        if from_point == None:
            return

        va = vec_sub(from_point, center)
        vb = vec_sub(to_point, center)
        ub = vec_ortho(va, vb)
        print vec_scal(va, vb) 
        angle = math.acos(vec_scal(va, vb)/(vec_norm(va)*vec_norm(vb)))
        def arc(t):
            alpha = t*angle
            ca = vec_mul(va, math.cos(alpha))
            cb = vec_mul(ub, math.sin(alpha))
            return vec_add(center, vec_add(ca, cb))

        self.add_path(arc, start=0.0, end=1.0, duration=duration)

    def add_pause(self, duration=1.0):
        if self.last_point == None:
            raise ValueError("Cannot use Path.add_pause before setting "
                             "the initial position with Path.add_segment")
        self.add_segment(to_point=self.last_point, duration=duration)

    def _check_path_piece(pp_idx, time):
        pp = self.path_pieces[pp_idx]
        t0s = self._get_t0s()
        if time >= t0s[pp_idx] and time < t0s[pp_idx + 1]:
            return pp

        else:
            return None

    def find_path_piece_idx(self, time):
        i = self.last_piece_accessed
        if i != None:
            # Check whether the path containing the time is the one which
            # was last used or the next one
            pp_try = self._check_path_piece(i)
            if pp_try != None:
                return i

            i = (i + 1) % len(self.path_pieces)
            pp_try = self._check_path_piece(i)
            if pp_try != None:
                self.last_piece_accessed = i
                return i

        t0s = self._get_t0s()
        l = len(self.t0s)
        for i in range(l):
            if time < self.t0s[i]:
                if i > 0:
                    return i - 1
                else:
                    return None
        return None

    def sample(self, time):
        pp_idx = self.find_path_piece_idx(time)
        if pp_idx == None:
            return None

        pp = self.path_pieces[pp_idx]
        renormalised_t = (time - self.t0s[pp_idx])/pp.duration
        parameter = pp.start + renormalised_t*(pp.end - pp.start)
        return pp.fn(parameter)

    def sample_all(self, start=0.0, framerate=25):
        max_time = self.get_max_time()
        sample_points = []
        def sample_fn(t):
            sample_points.append(self.sample(t))
        sample(sample_fn, max_time, start=start, framerate=framerate)
        return sample_points

if __name__ == '__main__':
    path = Path()
    path.add_segment([0, 0, 0], [10, 10, 10])
    path.add_segment(to_point=[10, 0, 10])

    ps = path.sample_all(framerate=25)
    for p in ps:
        print "%s %s" % (p[0], p[1])

