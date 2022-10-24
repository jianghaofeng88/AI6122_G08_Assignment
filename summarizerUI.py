from summarizer import *


if __name__ == '__main__':
    if (len(sys.argv) != 1):
        print("Usage: \npython summarizerUI.py\n")
        exit(1)
    print("Section 3.4 Review Summarizer")
    print("Developed by Jiang Haofeng\n2022/10/22\n--------------------------------------------\n")
    print("Here are the product types avaliable:")
    l = list(np.arange(len(TYPES)))
    d = dict(zip(l,TYPES))
    for key in d:
        print(f"{key}: {d[key]}") 
        
    next_or_exit = ""
    known_types = [0]*24
    while (next_or_exit != "exit"):
        typ = input("\nPlease choose the type of the product by index (e.g. 4, 12, 22, etc. However, due to large size, {0,1,2,3,6,14} is not recommended):")
        while not (typ.replace('-','',1).isdigit() and int(typ) >= -24 and int(typ) <= 23):
            print("The index must be an integer from -24 to 23")
            typ = input("Please choose the type of the product by index (e.g. 4, 12, 22, etc. However, due to large size, {0,1,2,3,6,14} is not recommended):")
        if known_types[int(typ)] == 0:
            writefile(typ)
            print(f"Initializing dataset for {regularize(typ)[0]}......")
            initialize_dataset(typ)
            print(f"Initializing dataset for {regularize(typ)[0]} is successful.")
            get_global_values()
            known_types[int(typ)] = (products_list(), product_id(), review_text())
        else:
            set_global_values(known_types[int(typ)][0], known_types[int(typ)][1], known_types[int(typ)][2])
        print(f"\nIn type {regularize(typ)[0]}, the sampled product ids are:")
        l=known_types[int(typ)][1]
        print(', '.join(l))
        i = input(f"Please choose the product id that you want to view the review summary (e.g. {l[0]}, {l[1]}):")
        while not (i in l):
            print("The asin must be in the above list")
            i = input(f"Please choose the product id that you want to view the review summary (e.g. {l[0]}, {l[1]}):")
        print(f"\nReview summary of the product {i}:")
        print('\n'.join(generate_summary(i, 10)))
        print("\n")
        next_or_exit = ""
        while (next_or_exit != "next" and next_or_exit != "exit"):
            next_or_exit = input("Enter 'next' to view other products, or enter 'exit' to exit:")       
    print("\nThanks for using!")
    exit(0)