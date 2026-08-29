import csv
from itertools import combinations
import matplotlib.pyplot as plt

csv_path = "/content/transactions.csv"
min_support = int(input("Enter minimum support count (e.g. 2): ").strip())
min_confidence = float(input("Enter minimum confidence as a decimal (e.g. 0.5): ").strip())
top_rules_to_plot = 10

transactions = []
with open(csv_path, 'r', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if not row:
            continue
        if len(row) == 1:
            cell = row[0].strip()
            if cell == "":
                continue
            if ',' in cell:
                items = [it.strip() for it in cell.split(',') if it.strip()]
            else:
                items = [cell]
        else:
            items = [it.strip() for it in row if it and it.strip()]
        transactions.append(items)

N = len(transactions)
if N == 0:
    raise SystemExit("No transactions read from CSV.")

def get_frequent_itemsets(transactions, k, prev_frequent=None):
    candidates = []
    if k == 1:
        counts = {}
        for t in transactions:
            for item in t:
                counts[item] = counts.get(item, 0) + 1
        for item, count in counts.items():
            if count >= min_support:
                candidates.append((frozenset([item]), count))
    else:
        items = set()
        for itemset, _ in prev_frequent:
            items.update(itemset)
        for cand in combinations(sorted(items), k):
            cand = frozenset(cand)
            count = sum(1 for t in transactions if cand.issubset(set(t)))
            if count >= min_support:
                candidates.append((cand, count))
    return candidates

k = 1
frequent_itemsets = []
prev_frequent = None
counts_by_size = {}
while True:
    current = get_frequent_itemsets(transactions, k, prev_frequent)
    if not current:
        break
    frequent_itemsets.extend(current)
    counts_by_size[k] = len(current)
    prev_frequent = current
    k += 1

freq_count = {}
freq_support = {}
for itemset, count in frequent_itemsets:
    freq_count[itemset] = count
    freq_support[itemset] = count / N

print("\nFrequent Itemsets (itemset : count, support):")
for itemset, count in sorted(frequent_itemsets, key=lambda x: (len(x[0]), -x[1], sorted(x[0]))):
    print(f"{set(itemset)} : {count}, {count}/{N} = {freq_support[itemset]:.3f}")

print("\nAssociation Rules (antecedent -> consequent) : support_count, confidence, lift")
rules = []

for itemset, count in frequent_itemsets:
    if len(itemset) <= 1:
        continue
    for r in range(1, len(itemset)):
        for antecedent in combinations(sorted(itemset), r):
            antecedent = frozenset(antecedent)
            consequent = itemset - antecedent
            antecedent_count = freq_count.get(antecedent, 0)
            consequent_count = freq_count.get(consequent, 0)
            if antecedent_count == 0:
                continue
            confidence = count / antecedent_count
            supp_consequent = consequent_count / N if consequent_count else sum(1 for t in transactions if consequent.issubset(set(t))) / N
            if supp_consequent == 0:
                lift = float('inf')
            else:
                lift = confidence / supp_consequent
            if confidence >= min_confidence:
                rules.append((antecedent, consequent, count, confidence, lift))

rules_sorted = sorted(rules, key=lambda x: (x[4], x[3]), reverse=True)
if not rules_sorted:
    print("No association rules found with these thresholds.")
else:
    for antecedent, consequent, support_count, confidence, lift in rules_sorted:
        print(f"{set(antecedent)} -> {set(consequent)} : support={support_count}, confidence={confidence:.3f}, lift={lift:.3f}")

if counts_by_size:
    ks = sorted(counts_by_size.keys())
    counts = [counts_by_size[k] for k in ks]
    plt.figure()
    plt.plot(ks, counts, marker='o')
    plt.title("Number of Frequent Itemsets vs Itemset Size (k)")
    plt.xlabel("Itemset size (k)")
    plt.ylabel("Number of frequent itemsets")
    plt.xticks(ks)
    plt.grid(True)
    plt.show()
else:
    print("No frequent itemsets to plot for itemset sizes.")

if rules_sorted:
    top = rules_sorted[:top_rules_to_plot]
    labels = [f"{set(a)}→{set(c)}" for (a, c, *_ ) in top]
    lifts = [r[4] for r in top]
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(lifts)), lifts)
    plt.title(f"Top {len(lifts)} Association Rules by Lift")
    plt.xlabel("Rule (antecedent → consequent)")
    plt.ylabel("Lift")
    plt.xticks(range(len(lifts)), labels, rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
else:
    print("No rules to plot by lift.")
