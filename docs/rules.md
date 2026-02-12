# Testability Rules Documentation

This document provides detailed explanations of all 12 testability rules, including detection criteria, penalty points, and specific refactoring suggestions.

## Table of Contents

- [Red Flag Rules](#red-flag-rules)
- [Standard Rules](#standard-rules)
- [Implementation Details](#implementation-details)

---

## Red Flag Rules

Red flag rules indicate structural issues that should always be addressed, regardless of the overall score.

### 1. Constructor Side Effects (-15 points)

**What it detects**: Constructors that perform I/O operations, network calls, database connections, or other side effects.

**Why it's a problem**: 
- Makes object instantiation difficult to test
- Creates hidden dependencies
- Violates the principle that constructors should only initialize object state
- Makes it impossible to create objects in isolation for testing

**Detection criteria**:
- File operations in `__init__` methods
- Network calls in constructors
- Database connections or queries
- Process/thread creation
- Import statements in constructors
- Global state mutations

**Example violations**:
```python
# BAD: File I/O in constructor
class ConfigLoader:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:  # 🚨 Red flag
            self.config = json.load(f)

# BAD: Network call in constructor  
class APIClient:
    def __init__(self, base_url):
        self.session = requests.Session()  # 🚨 Red flag
        self.base_url = base_url

# BAD: Database connection in constructor
class UserRepository:
    def __init__(self, connection_string):
        self.db = psycopg2.connect(connection_string)  # 🚨 Red flag
```

**Refactoring suggestions**:
1. **Use dependency injection**:
```python
class ConfigLoader:
    def __init__(self, config_data):  # Inject config data
        self.config = config_data

# Usage
with open('config.json', 'r') as f:
    config_data = json.load(f)
loader = ConfigLoader(config_data)
```

2. **Use factory pattern**:
```python
class ConfigLoader:
    def __init__(self):
        self.config = None
    
    @classmethod
    def from_file(cls, config_path):
        loader = cls()
        with open(config_path, 'r') as f:
            loader.config = json.load(f)
        return loader
```

3. **Separate initialization**:
```python
class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = None
    
    def connect(self):
        self.session = requests.Session()
```

### 2. Global State Mutation (-10 points)

**What it detects**: Functions that modify global variables or shared state.

**Why it's a problem**:
- Creates hidden dependencies between tests
- Makes test order important
- Causes test isolation failures
- Makes code behavior unpredictable

**Detection criteria**:
- `global` statements in functions
- Assignment to module-level variables
- Modification of singleton objects
- Registry or cache modifications

**Example violations**:
```python
# BAD: Global variable mutation
counter = 0

def increment_counter():
    global counter  # 🚨 Red flag
    counter += 1

# BAD: Module-level state mutation
config = {}

def update_config(key, value):
    config[key] = value  # 🚨 Red flag

# BAD: Singleton modification
class Database:
    _instance = None
    
    @classmethod
    def set_instance(cls, instance):
        cls._instance = instance  # 🚨 Red flag
```

**Refactoring suggestions**:
1. **Use dependency injection**:
```python
class Counter:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1

# Pass counter instance to functions
def process_data(counter, data):
    counter.increment()
    # ... process data
```

2. **Use context managers**:
```python
class ConfigContext:
    def __init__(self, initial_config=None):
        self.config = initial_config or {}
    
    def __enter__(self):
        return self.config
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.config.clear()

# Usage
with ConfigContext() as config:
    config['key'] = 'value'
    # ... use config
```

3. **Create stateless functions**:
```python
def update_config(config, key, value):
    new_config = config.copy()
    new_config[key] = value
    return new_config

# Usage
config = {}
config = update_config(config, 'key', 'value')
```

### 3. Non-Deterministic Time Usage (-10 points)

**What it detects**: Functions that use current time, making behavior non-deterministic.

**Why it's a problem**:
- Makes tests non-reproducible
- Causes flaky tests
- Makes assertions difficult
- Hides timing-related bugs

**Detection criteria**:
- `time.time()`, `time.sleep()`, `time.monotonic()`
- `datetime.now()`, `datetime.today()`, `datetime.utcnow()`
- `date.today()`
- Any time-based logic

**Example violations**:
```python
# BAD: Using current time
def get_timestamp():
    return time.time()  # 🚨 Red flag

# BAD: Time-based logic
def is_expired(created_time):
    return datetime.now() > created_time  # 🚨 Red flag

# BAD: Sleep in logic
def retry_with_delay():
    time.sleep(1)  # 🚨 Red flag
    return attempt_operation()
```

**Refactoring suggestions**:
1. **Inject time as parameter**:
```python
def get_timestamp(current_time=None):
    if current_time is None:
        current_time = time.time()
    return current_time

def is_expired(created_time, current_time=None):
    if current_time is None:
        current_time = datetime.now()
    return current_time > created_time
```

2. **Use time abstraction layer**:
```python
class TimeProvider:
    @staticmethod
    def now():
        return datetime.now()
    
    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)

def is_expired(created_time, time_provider=TimeProvider):
    return time_provider.now() > created_time
```

3. **Create deterministic versions for testing**:
```python
def get_timestamp(time_func=time.time):
    return time_func()

# In tests
def test_get_timestamp():
    mock_time = lambda: 1234567890
    assert get_timestamp(mock_time) == 1234567890
```

### 4. Mixed I/O and Logic (-8 points)

**What it detects**: Functions that combine business logic with I/O operations.

**Why it's a problem**:
- Violates separation of concerns
- Makes unit testing difficult
- Couples business logic to I/O details
- Reduces code reusability

**Detection criteria**:
- File operations combined with calculations
- Network calls mixed with business logic
- Database queries embedded in logic
- Console I/O in business functions

**Example violations**:
```python
# BAD: File I/O mixed with logic
def process_and_save(data):
    result = complex_calculation(data)  # Logic
    with open('output.txt', 'w') as f:  # I/O
        f.write(str(result))  # Mixed

# BAD: Network call mixed with logic
def fetch_and_process(url):
    response = requests.get(url)  # I/O
    return transform_data(response.json())  # Mixed

# BAD: Database query mixed with logic
def calculate_user_stats(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))  # I/O
    user = cursor.fetchone()
    return user['orders'] * user['rate']  # Mixed
```

**Refactoring suggestions**:
1. **Separate I/O and logic**:
```python
def process_data(data):
    return complex_calculation(data)

def save_result(result, filename):
    with open(filename, 'w') as f:
        f.write(str(result))

# Usage
data = load_data()
result = process_data(data)
save_result(result, 'output.txt')
```

2. **Use repository pattern**:
```python
class UserRepository:
    def get_user(self, user_id):
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

def calculate_user_stats(user_repo, user_id):
    user = user_repo.get_user(user_id)
    return user['orders'] * user['rate']
```

3. **Use command/query separation**:
```python
class DataProcessor:
    def process(self, data):
        return complex_calculation(data)

class DataSaver:
    def save(self, result, filename):
        with open(filename, 'w') as f:
            f.write(str(result))
```

### 5. Exception-Driven Control Flow (-5 points)

**What it detects**: Using exceptions for normal program flow instead of error handling.

**Why it's a problem**:
- Obscures actual logic paths
- Makes code harder to understand
- Performance overhead
- Hides real error conditions

**Detection criteria**:
- Empty except blocks
- Broad exception catching
- Using exceptions for control flow
- Exception-based loops

**Example violations**:
```python
# BAD: Exception for control flow
def get_first_item(items):
    try:
        return items[0]
    except IndexError:  # 🚨 Red flag - using exception for control flow
        return None

# BAD: Empty except block
def risky_operation():
    try:
        do_something()
    except:  # 🚨 Red flag - empty except
        pass

# BAD: Broad exception handling
def process_data(data):
    try:
        return transform(data)
    except Exception:  # 🚨 Red flag - too broad
        return None
```

**Refactoring suggestions**:
1. **Use proper control flow**:
```python
def get_first_item(items):
    if items:  # Check condition instead of exception
        return items[0]
    return None
```

2. **Handle specific exceptions**:
```python
def process_data(data):
    try:
        return transform(data)
    except ValueError as e:  # Specific exception
        logger.error(f"Invalid data: {e}")
        return None
```

3. **Use early returns or guards**:
```python
def process_data(data):
    if not data:
        return None
    
    if not is_valid(data):
        return None
    
    return transform(data)
```

---

## Standard Rules

Standard rules indicate testability issues that should be addressed based on their impact.

### 6. Direct File I/O in Logic (-10 points)

**What it detects**: File operations embedded in business logic functions.

**Why it's a problem**:
- Requires file system setup for testing
- Makes tests dependent on external files
- Reduces test portability
- Complicates test data management

**Detection criteria**:
- `open()`, `read()`, `write()` in business logic
- File path operations
- Directory operations in logic functions

**Example violations**:
```python
# BAD: File I/O in business logic
def calculate_total(filename):
    with open(filename, 'r') as f:  # File I/O in logic
        data = f.read()
    return sum(map(int, data.split()))
```

**Refactoring suggestions**:
1. **Pass file handles as parameters**:
```python
def calculate_total(data):
    return sum(map(int, data.split()))

def calculate_total_from_file(filename):
    with open(filename, 'r') as f:
        data = f.read()
    return calculate_total(data)
```

### 7. Randomness Usage (-10 points)

**What it detects**: Functions using random number generators.

**Why it's a problem**:
- Makes test results unpredictable
- Causes flaky tests
- Difficult to assert expected outcomes
- Hides deterministic bugs

**Detection criteria**:
- `random.*` functions
- `numpy.random.*` functions
- `uuid.uuid*()` functions
- `secrets.*` functions

**Example violations**:
```python
# BAD: Randomness in logic
def generate_random_id():
    return uuid.uuid4()  # Unpredictable for testing
```

**Refactoring suggestions**:
1. **Inject random generator**:
```python
def generate_random_id(uuid_generator=uuid.uuid4):
    return uuid_generator()

# In tests
def test_generate_random_id():
    mock_uuid = lambda: UUID('12345678-1234-5678-1234-567812345678')
    assert str(generate_random_id(mock_uuid)) == '12345678-1234-5678-1234-567812345678'
```

### 8. External Dependency Count (-5 points per distinct type)

**What it detects**: Functions with dependencies on external systems.

**Why it's a problem**:
- Increases test setup complexity
- Requires mocking or test doubles
- Reduces test reliability
- Makes tests slower

**Detection criteria**:
- File system operations
- Network calls
- Database access
- OS-level operations
- External service calls

**Example violations**:
```python
# BAD: Multiple external dependencies
def process_and_upload(data, filepath, api_url):
    with open(filepath, 'w') as f:  # File system
        f.write(data)
    requests.post(api_url, data=data)  # Network
    return True
```

**Refactoring suggestions**:
1. **Use dependency injection**:
```python
def process_data(data, file_writer, http_client):
    file_writer.write(data)
    http_client.post(data)
    return True
```

### 9. Hidden Dependencies via Imports-in-Function (-5 points)

**What it detects**: Import statements inside functions.

**Why it's a problem**:
- Hides dependencies from module interface
- Makes dependency analysis difficult
- Increases import overhead
- Reduces code clarity

**Example violations**:
```python
# BAD: Import inside function
def process_json(data):
    import json  # Hidden dependency
    return json.loads(data)
```

**Refactoring suggestions**:
1. **Move imports to module level**:
```python
import json

def process_json(data):
    return json.loads(data)
```

### 10. Excessive Parameter Count (-5 points)

**What it detects**: Functions with more than 5 parameters.

**Why it's a problem**:
- Indicates high complexity
- Makes function calls difficult
- Suggests poor cohesion
- Complicates testing

**Example violations**:
```python
# BAD: Too many parameters
def complex_function(a, b, c, d, e, f, g):
    return a + b + c + d + e + f + g
```

**Refactoring suggestions**:
1. **Use parameter objects**:
```python
class ProcessConfig:
    def __init__(self, a, b, c, d, e, f, g):
        self.a = a
        self.b = b
        # ... etc

def complex_function(config):
    return config.a + config.b + config.c + config.d + config.e + config.f + config.g
```

### 11. Low Observability (-5 points)

**What it detects**: Functions without return values, logging, or assertions.

**Why it's a problem**:
- Difficult to verify behavior
- Hard to debug issues
- Poor error visibility
- Unclear side effects

**Example violations**:
```python
# BAD: No observability
def process_data(data):
    result = complex_calculation(data)
    # No return, no logging, no assertions
```

**Refactoring suggestions**:
1. **Add return values**:
```python
def process_data(data):
    result = complex_calculation(data)
    return result  # Observable result
```

2. **Add logging**:
```python
def process_data(data):
    result = complex_calculation(data)
    logging.info(f"Processed data: {result}")
    return result
```

### 12. Branch Explosion Risk (-2 points per branch after 3)

**What it detects**: Functions with excessive conditional branching.

**Why it's a problem**:
- Increases test complexity
- Suggests high cognitive load
- Makes code hard to maintain
- Indicates need for refactoring

**Example violations**:
```python
# BAD: Too many branches
def complex_logic(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
    return 0
```

**Refactoring suggestions**:
1. **Extract conditions**:
```python
def should_process(a, b, c, d, e):
    return all(x > 0 for x in [a, b, c, d, e])

def complex_logic(a, b, c, d, e):
    if should_process(a, b, c, d, e):
        return a + b + c + d + e
    return 0
```

---

## Implementation Details

### Rule Priority

1. **Red flags first**: Always address red flag violations before other issues
2. **High impact rules**: Focus on rules with higher point deductions
3. **Frequency**: Address rules that appear frequently across the codebase
4. **Context**: Consider the specific context and requirements of your project

### Scoring Algorithm

- **Baseline**: 100 points per function
- **Deductions**: Subtract points for each violation
- **Floor**: Scores never go below 0
- **Aggregation**: File scores use the worst function score

### Quality Gates

Recommended minimum scores:
- **New code**: 80+ points (Healthy)
- **Existing code**: 60+ points (Caution)
- **Critical systems**: 85+ points

### Integration Tips

1. **Gradual improvement**: Don't try to fix everything at once
2. **Team consensus**: Agree on which rules to prioritize
3. **Automation**: Integrate with CI/CD for consistent enforcement
4. **Education**: Help team understand the "why" behind each rule
5. **Exceptions**: Document when and why violations are acceptable

### Common Misconceptions

- **"All violations must be fixed"**: Some violations may be acceptable in specific contexts
- **"High score = good code"**: Score is a guide, not an absolute measure of quality
- **"Rules are rigid"**: Adapt rules to your specific project needs
- **"Automation replaces code review"**: Use the tool to enhance, not replace, human review
