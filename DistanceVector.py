#!/usr/bin/env python3

import sys
import copy

# I defined infinity as 1,000,000,000
INF = 10**9

# uncomment the following line to redirect the output to a file
sys.stdout = open('sampleoutput5', 'w')

def parse_input():
    """
    (sample_input) -> 
        [routers] : list of str
        [links_initial] : list of tuples
        [links_updated] : list of tuples
        is_updated : bool

    parse the three sections from the input file.
    1. list of router names until "START"
    2. list of links <A> <B> <cost> until "UPDATE"
    3. list of link-changes <A> <B> <cost> until "END"

    """
    routers = []
    links_initial = []
    links_update = []
    is_updated = False

    # 1 - read router names until "START"
    for line in sys.stdin:
        line = line.strip()
        if line == "START":
            break
        if line != "":
            routers.append(line)

    # 2 - read initial links until "UPDATE"
    for line in sys.stdin:
        line = line.strip()
        if line == "UPDATE":
            break
        if not line:
            continue
        A, B, cost = line.split()    # split 2 router names and cost
        links_initial.append((A, B, int(cost)))

    # 3 - read link changes until "END"
    for line in sys.stdin:
        line = line.strip()
        if line == "END":
            break
        if not line:
            continue
        A, B, cost = line.split()    # split 2 router names and cost
        links_update.append((A, B, int(cost)))
    
    # if updates exist, dv must be run again. note down this for future use 
    if len(links_update) > 0:
        is_updated = True


    return routers, links_initial, links_update, is_updated
    """    
    print(routers)
    print("------------")
    print(links_initial)
    print("------------")
    print(links_update)
    """

def build_adjacency(routers, links):
    """
    (list of routers, list of links (A,B,cost)) ->
        {router : {neighbour: link cost, neighbour: link cost,...},
         router : {neighbour: link cost, neighbour: link cost,...} 
        ... }

    build a dictionary where
        for each router x,
        adj[x] is a dictionary of x's neighbours and costs
    
    test output:
    >>> adj = build_adjacency(routers from sample toplogy, links_initial from sample topology)
    {'X': {'Z': 9, 'Y': 3}, 'Y': {'X': 3, 'Z': 4}, 'Z': {'X': 9, 'Y': 4}}

    """
    # initialise dict of routers : {}
    adj = {r: {} for r in routers}
    # print(adj)

    
    for A, B, cost in links:

        # handle addition of new routers 
        if A not in adj:
            adj[A] = {}
        if B not in adj:
            adj[B] = {}
    
        # remove link if cost == -1
        if cost == -1:
            adj[A].pop(B, None)
            adj[B].pop(A, None)
            
        # add neighbour and its link cost
        else:
            adj[A][B] = cost
            adj[B][A] = cost

    return adj

def run_DV(routers, adj, D_prev=None, t_start=0):
    """
    Run the Distance Vector algorithm AND print the tables.

    (list of routers, adjacency dictionary, optional previous distance vector, start time t_start) ->
        (final distance vector D_prev, next time step)
    
    If D_prev is None, initializes from scratch (t=0).
    Otherwise, continues from D_prev starting at t_start.

    Process:
        1. Initalise the distance vector table D_prev (if not proviced)
        2. LOOP:
            - for each router:
                - print current distance table.
                - compute the new best distances to all destinations through neighbours
            - if no distance changed in the round -> convergance reached -> stop
            - otherwise -> updatre D_prev and continue to next round.
        3. After convergance, print final routing table for each router.

    ON UPDATE:
        main() will call this function again
        with previous distance vector and t value.
    """
    routers = sorted(routers)

    # 1 - initialise if no prev state given
    if D_prev is None:
        D_prev = {
            x: { y: (0 if x == y else INF) for y in routers }
            for x in routers
        }
    t = t_start

    # 2 - main loop: iterate until no distance changes in a full round
    while True:

        # - print distance tables at t
        for x in routers:
            hops = [v for v in routers if v != x]
            print(f"Distance Table of router {x} at t={t}:")
            # header row - all possible destinations
            print("     " + "   ".join(hops))

            # for each destination, show cost via every other router as a next hop. INF if unreachable
            for dest in hops:
                row = []
                # next_hop is next hop
                for next_hop in hops:
                    cost_through = adj[x].get(next_hop, INF) + D_prev[next_hop][dest]
                    row.append(str(cost_through) if cost_through < INF else "INF")
                print(f"{dest}   " + "   ".join(row))
            print() # blank line
        
        # - compute new distance vectors from previous D_prev
        D_cur = {
            x: { y: (0 if x == y else INF) for y in routers }
            for x in routers
        }
        
        changed = False
        # default false -> no costs changed anywhere 
        # if any router found a better cost any destination -> changed = True

        for x in routers:
            for dest in routers:
                if x == dest:
                    continue    # distance to self must remain 0
                best = INF
                # only real neighbours can forward
                for next_hop, link_cost in adj[x].items():
                    c = link_cost + D_prev[next_hop][dest]
                    if c < best:
                        best = c
                D_cur[x][dest] = best
                if best != D_prev[x][dest]:
                    changed = True
                    # found a better cost destination

        # 3 - check convergence
        # no router updated its table → the network has converged 
        if not changed:
            break

        # prepare for next round
        D_prev = D_cur
        t += 1
    
    # 4 - print final routing tables
    for x in routers:
        print(f"Routing Table of router {x}:")
        for dest in [r for r in routers if r != x]:
            total = D_cur[x][dest]
            if total >= INF:
                print(f"{dest},INF,INF") # unreachable destination
            else:
                # choose alphabetically next hop
                best_next_hop, best_cost = None, INF
                for next_hop in sorted(adj[x].keys()):
                    c = adj[x][next_hop] + D_cur[next_hop][dest]
                    if c < best_cost:
                        best_cost, best_next_hop = c, next_hop
                print(f"{dest},{best_next_hop},{best_cost}")
        print() # blank line

    
    # return the final distance vectors and the next time index
    # essentially returning the state so an UPDATE can continue from this
    return D_prev, t+1

def main():
    """
    main driver function.

    process:
    1. parse input using parse_input():
        - routers
        - initial links
        - update links (if any)
        - is_updated boolean
    2. build initial adjacency dictionary.
    3. run Distance Vector algorithm on initial topology (run_DV).
    4. If an UPDATE section exists:
        - add any new routers
        - build updated adjacency dictionary
        - run Distance Vector again, continuing from previous state.

    prints output to stdout / output2.txt
    """

    routers, links_initial, links_update, is_updated = parse_input()

    # -- initial convergence 
    adj0 = build_adjacency(routers, links_initial)
    D_prev, next_t = run_DV(routers, adj0)

    # -- IF there was an UPDATE, apply and continue 
    if is_updated:
        # allow any new routers in the update
        for A, B, cost in links_update:
            if cost != -1:
                if A not in routers:
                    routers.append(A)
                if B not in routers:
                    routers.append(B)
        
        # build updated adjacency dict and run DV again
        adj1 = build_adjacency(routers, links_initial + links_update)
        run_DV(routers, adj1, D_prev, next_t)


if __name__ == "__main__":
    main()
    