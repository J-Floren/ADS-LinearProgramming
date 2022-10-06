
from intervaltree import Interval, IntervalTree

def parse_blackout(line: str):
    [start, duration] = map(float, line.split(","))
    return start, start + duration

def parse_input(path: str) -> tuple[list[float], list[tuple[float, float]], float, list[float]]:
    with open(path, "r") as f:
        num_pictures = int(f.readline())
        pictures = [float(f.readline()) for _ in range(num_pictures)]

        num_blackouts = int(f.readline())
        blackouts = [parse_blackout(f.readline()) for _ in range(num_blackouts)]
        blackouts.sort()

        expected_total_cost = float(f.readline())
        positions = [float(f.readline()) for _ in range(num_pictures)]

        print("Pictures:", pictures)
        print("Blackouts:", blackouts)
        print("ExpectedTotalCost:", expected_total_cost)
        

        return pictures, blackouts, expected_total_cost, positions

pictures, blackouts, expected_total_cost, positions = parse_input("assignment/bigger.txt")

assert len(pictures) == len(positions)
tree = IntervalTree([Interval(a, b) for a, b in blackouts])

for pos, size in zip(positions, pictures):
    assert pos >= 0
    assert sorted(tree[pos:pos+size]) == []
    tree.add(Interval(pos, pos+size))



