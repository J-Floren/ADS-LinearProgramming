from random import uniform
from sys import argv

def random_array(length: int, low: float, high: float, decimals: int) -> list[float]:
  return [round(uniform(low, high), decimals) for _ in range(length)]

def get_blackouts(knapsacks: list[float], decimals: int) -> list[float]:
  blackouts = []
  total_time = 0

  for k in knapsacks:
    blackouts.append(round(k + total_time, decimals))
    total_time += k + 1

  return blackouts

def main() -> None:
  if len(argv) != 9:
    print(f"Usage: {argv[0]} Npics Lpics Hpics Nknaps Lknaps Hknaps Dpics Dknaps")
    exit(1)

  num_pictures = int(argv[1])
  low_pictures = float(argv[2])
  high_pictures = float(argv[3])

  num_knapsacks = int(argv[4])
  low_knapsacks = float(argv[5])
  high_knapsacks = float(argv[6])

  decimals_pictures = int(argv[7])
  decimals_knapsacks = int(argv[8])

  pictures = random_array(num_pictures, low_pictures, high_pictures, decimals_pictures)
  knapsacks = random_array(num_knapsacks, low_knapsacks, high_knapsacks, decimals_knapsacks)
  blackouts = get_blackouts(knapsacks, decimals_knapsacks)

  print(len(pictures))
  for p in pictures:
    print(p)

  print(len(blackouts))
  for b in blackouts:
    print(f"{b}, 1")

if __name__ == "__main__":
  main()
