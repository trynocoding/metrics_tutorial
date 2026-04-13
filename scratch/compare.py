import re

# 1. Parse dcs.txt
metrics_raw = set()
with open('raw_data/dcs.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('# TYPE '):
            parts = line.split()
            if len(parts) >= 3:
                name = parts[2]
                if not name.endswith('_created'):
                    metrics_raw.add(name)

# 2. Parse dcs_metrics.md
metrics_md = set()
with open('docs/dcs_metrics.md', 'r', encoding='utf-8') as f:
    for line in f:
        m = re.match(r'^\|\s*`([^`]+)`', line)
        if m:
            metrics_md.add(m.group(1))

# Compare
missing_in_md = metrics_raw - metrics_md
extra_in_md = metrics_md - metrics_raw

print('Missing in MD (in raw but not in MD):')
for m in sorted(missing_in_md):
    print(m)

print('\nExtra in MD (in MD but not in raw):')
for m in sorted(extra_in_md):
    print(m)

print('\nTotal in raw (excluding _created):', len(metrics_raw))
print('Total in MD:', len(metrics_md))
