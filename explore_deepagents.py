import deepagents
import inspect

print('Available modules in deepagents:')
for m in dir(deepagents):
    if not m.startswith('_'):
        print(f'- {m}')

print('\nTrying to import backends module...')
try:
    import deepagents.backends
    print('\nAvailable components in deepagents.backends:')
    for c in dir(deepagents.backends):
        if not c.startswith('_'):
            print(f'- {c}')
except ImportError as e:
    print(f'Error importing backends: {e}')

# Let's also check if there are other submodules
print('\nChecking for other submodules...')
for m in dir(deepagents):
    if not m.startswith('_'):
        try:
            submodule = getattr(deepagents, m)
            if inspect.ismodule(submodule):
                print(f'\n- {m} (submodule):')
                for item in dir(submodule):
                    if not item.startswith('_'):
                        print(f'  - {item}')
        except Exception as e:
            print(f'\n- {m} (not a submodule or error accessing): {e}')