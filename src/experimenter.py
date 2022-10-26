import os
import formula_2
import re
import numpy


def main():
    exp_path = "../experiment_instances_2"
    experiment_files = [os.path.join(exp_path, f) for f in os.listdir(exp_path) if
                        os.path.isfile(os.path.join(exp_path, f))]

    with open("../exp_results.csv", "w", encoding="UTF-8") as f:
        f.write("case_number;Num_images;Num_blackouts;optimal_time;time_to_solve_F2;total_cost_F2;number_full_knapsacks;number_used_knapsacks;number_all_knapsacks\n")

    with open("../exp_results.csv", "a", encoding="UTF-8") as f1:
        for file in experiment_files:
            skips_pattern = "(4_[1-5]|10_4|12_2)" # skip because they are either too long to run or in a wrong format
            if not re.search(skips_pattern, file):
                print(file)
                with open(file, "r", encoding="utf-8") as f2:
                    num_pictures = int(f2.readline())
                    for _ in range(num_pictures):
                        next(f2)
                    num_blackouts = int(f2.readline())
                    for _ in range(num_blackouts):
                        next(f2)
                    opt_val = round(float(f2.readline()), 3)

                times = []
                for i in range(5):
                    solve_time_F2, cost_F2, num_full_knaps, num_used_knaps, num_knapsacks = formula_2.main(file)
                    times.append(solve_time_F2)
                avg_time_to_solve = numpy.mean(times)
                file_name = re.search('([0-9_]{3,5}\.txt)$', file).group(1)
                f1.write(f"{file_name};{num_pictures};{num_blackouts};{opt_val};{avg_time_to_solve};{round(cost_F2, 3)};{num_full_knaps};{num_used_knaps};{num_knapsacks}\n")


if __name__ == "__main__":
    main()

