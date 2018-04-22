from multiprocessing import Pool

def a(x):
    with Pool(10) as p:
        return p.map(
            str,
            [10, 11, 12] * x,
        )

with Pool(10) as p_:
    print(
        p_.map(
            a,
            [1, 2, 3]
        ),
    )
