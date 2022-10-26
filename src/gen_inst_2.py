import random


def main():
    num_images = int(input("number of images: "))
    min_image_size = float(input("minimum image size:"))
    max_image_size = float(input("maximum image size:"))
    num_blackouts = int(input("number of blackouts"))
    decimal_points = 2

    items, indexes_images, indexes_blackouts = [], [], []
    C, i, previous_was_blackout = random.uniform(1.0, 2.0), 0, False

    # 'items' holds all images and blackouts. Which item is an image and which is a blackout is selected randomly.
    # C / x is the chance of an item being a blackout. C increases with the number of consecutive images
    while len(indexes_images) < num_images:
        if random.random() < C / 20 and len(indexes_blackouts) < num_blackouts and not previous_was_blackout:
            items.append(round(random.uniform(min_image_size, max_image_size), decimal_points))
            indexes_blackouts.append(i)
            C = random.uniform(1.0, 2.0)
            previous_was_blackout = True
        else:
            indexes_images.append(i)
            items.append(round(random.uniform(min_image_size, max_image_size), decimal_points))
            previous_was_blackout = False
            C += 1
        i += 1

    # distinguish between images and blackouts and also calculate the cumulative cost
    optimum, images, blackouts, output_image_start_positions = 0.0, [], [], []
    for i in range(len(items)):
        if i in indexes_images:
            images.append(items[i])
            output_image_start_positions.append(optimum)
        elif i in indexes_blackouts:
            blackouts.append((optimum, items[i]))
        optimum = optimum + items[i]

    # if the first part generated fewer blackouts than required by the prompt, generate more and put them at the end
    count = optimum + random.uniform(0, max_image_size)
    for i in range(num_blackouts - len(indexes_blackouts)):
        new_blackout = random.uniform(min_image_size, max_image_size)
        new_knapsack = random.uniform(min_image_size, max_image_size) * random.uniform(1, 5)
        blackouts.append((count, new_blackout))
        count += new_blackout + new_knapsack

    images = [str(round(i, decimal_points)) for i in images]
    random.shuffle(images)
    blackouts = [f"{round(b[0], decimal_points)}, {round(b[1], decimal_points)}" for b in blackouts]
    random.shuffle(blackouts)
    output_image_start_positions = [str(round(i, decimal_points)) for i in output_image_start_positions]

    INPUT = str(len(images)) + "\n" + "\n".join(images) + "\n" + str(len(blackouts)) + "\n" + "\n".join(blackouts)
    OUTPUT = str(round(optimum, 3)) + "\n" + "\n".join(output_image_start_positions)
    print("\nINPUT:", INPUT, OUTPUT, sep="\n")


if __name__ == "__main__":
    main()
