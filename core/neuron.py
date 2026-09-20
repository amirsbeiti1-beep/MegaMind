import json
import math
from datetime import datetime


# ============================================================
# MEGAMIND
# Sovereign Reasoning Core
# Version 5.1
# ============================================================

KNOWLEDGE_FILE = "core/knowledge.json"
VERSION = 5.1


# ============================================================
# KNOWLEDGE STRUCTURE
# ============================================================

def default_knowledge():
    return {
        "version": VERSION,
        "principles": [],
        "concepts": [],
        "experiences": [],
        "strategies": [],
        "experiments": []
    }


def load_knowledge():
    try:
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
            knowledge = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        knowledge = default_knowledge()

    if not isinstance(knowledge, dict):
        knowledge = default_knowledge()

    defaults = default_knowledge()

    for key, default_value in defaults.items():

        if key not in knowledge:

            if isinstance(default_value, list):
                knowledge[key] = []

            else:
                knowledge[key] = default_value

    migrate_knowledge(knowledge)

    return knowledge


def save_knowledge(knowledge):

    with open(
        KNOWLEDGE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            knowledge,
            file,
            indent=4,
            ensure_ascii=False,
            allow_nan=False
        )


# ============================================================
# MIGRATION
# ============================================================

def migrate_knowledge(knowledge):

    # --------------------------------------------------------
    # PRINCIPLES
    # --------------------------------------------------------

    for principle in knowledge["principles"]:

        if not isinstance(principle, dict):
            continue

        principle.setdefault(
            "instances",
            []
        )

        # Old V1-V3 format:
        #
        # "model": {...}
        #
        # becomes:
        #
        # "instances": [
        #     {"model": {...}}
        # ]

        if "model" in principle:

            model = principle.get("model")

            if isinstance(model, dict):

                already_exists = any(
                    models_equal(
                        instance.get("model"),
                        model
                    )
                    for instance
                    in principle["instances"]
                    if isinstance(instance, dict)
                )

                if not already_exists:

                    principle["instances"].append({
                        "model": model,
                        "average_error":
                            principle.get(
                                "average_error",
                                0.0
                            )
                    })

            principle.pop(
                "model",
                None
            )

            principle.pop(
                "average_error",
                None
            )

        principle.setdefault(
            "times_discovered",
            len(principle["instances"])
        )

        principle.setdefault(
            "description",
            "A reusable relationship discovered from data."
        )

    # --------------------------------------------------------
    # EXPERIMENTS → PRINCIPLES
    # --------------------------------------------------------

    for experiment in knowledge["experiments"]:

        if not isinstance(experiment, dict):
            continue

        model = experiment.get("model")

        if not isinstance(model, dict):
            continue

        model_type = model.get("type")

        if not model_type:
            continue

        principle_type = (
            model_type
            + "_relationship"
        )

        principle = next(
            (
                p
                for p in knowledge["principles"]
                if isinstance(p, dict)
                and p.get("type")
                == principle_type
            ),
            None
        )

        if principle is None:

            principle = {
                "type":
                    principle_type,

                "description":
                    "A reusable relationship discovered from data.",

                "instances":
                    [],

                "times_discovered":
                    0
            }

            knowledge["principles"].append(
                principle
            )

        already_exists = any(
            models_equal(
                instance.get("model"),
                model
            )
            for instance
            in principle["instances"]
            if isinstance(instance, dict)
        )

        if not already_exists:

            principle["instances"].append({
                "model":
                    model,

                "average_error":
                    experiment.get(
                        "average_error",
                        0.0
                    )
            })

    # --------------------------------------------------------
    # CONCEPTS
    # --------------------------------------------------------

    for concept in knowledge["concepts"]:

        if not isinstance(concept, dict):
            continue

        concept.setdefault(
            "name",
            "unknown_concept"
        )

        concept.setdefault(
            "description",
            "A concept learned from experience."
        )

        concept.setdefault(
            "category",
            "general"
        )

        concept.setdefault(
            "times_observed",
            1
        )

        concept.setdefault(
            "experience_ids",
            []
        )

        concept.setdefault(
            "confidence",
            1.0
        )

    # --------------------------------------------------------
    # EXPERIENCES
    # --------------------------------------------------------

    for index, experience in enumerate(
        knowledge["experiences"],
        start=1
    ):

        if not isinstance(experience, dict):
            continue

        experience.setdefault(
            "id",
            index
        )

        experience.setdefault(
            "timestamp",
            now()
        )

        experience.setdefault(
            "context",
            {}
        )

    # --------------------------------------------------------
    # STRATEGIES
    # --------------------------------------------------------

    for strategy in knowledge["strategies"]:

        if not isinstance(strategy, dict):
            continue

        strategy.setdefault(
            "type",
            "unknown"
        )

        strategy.setdefault(
            "attempts",
            0
        )

        strategy.setdefault(
            "successes",
            0
        )

        strategy.setdefault(
            "failures",
            0
        )

        strategy.setdefault(
            "success_rate",
            calculate_success_rate(
                strategy["successes"],
                strategy["attempts"]
            )
        )

    knowledge["version"] = VERSION


# ============================================================
# UTILITIES
# ============================================================

def now():

    return datetime.now().isoformat(
        timespec="seconds"
    )


def calculate_success_rate(
    successes,
    attempts
):

    if attempts <= 0:
        return 0.0

    return successes / attempts


def models_equal(
    model_a,
    model_b,
    tolerance=0.00000001
):

    if not isinstance(model_a, dict):
        return False

    if not isinstance(model_b, dict):
        return False

    if model_a.get("type") != model_b.get("type"):
        return False

    model_type = model_a.get("type")

    if model_type == "linear":

        try:

            return (
                abs(
                    model_a["weight"]
                    - model_b["weight"]
                ) < tolerance

                and

                abs(
                    model_a["bias"]
                    - model_b["bias"]
                ) < tolerance
            )

        except (KeyError, TypeError):
            return False

    if model_type == "constant":

        try:

            return abs(
                model_a["value"]
                - model_b["value"]
            ) < tolerance

        except (KeyError, TypeError):
            return False

    return model_a == model_b


# ============================================================
# ARITHMETIC REASONING
# ============================================================

def solve_arithmetic(demand):

    if not isinstance(demand, str):
        return None

    text = (
        demand
        .replace("×", "*")
        .replace("÷", "/")
        .replace("?", "")
        .strip()
    )

    if not text:
        return None

    allowed = set(
        "0123456789+-*/(). %"
    )

    if any(
        character not in allowed
        for character in text
    ):
        return None

    try:

        result = eval(
            text,
            {
                "__builtins__": {}
            },
            {}
        )

    except Exception:
        return None

    if not isinstance(
        result,
        (int, float)
    ):
        return None

    if not math.isfinite(result):
        return None

    return {
        "answer": result,
        "reasoning":
            "Evaluated the arithmetic expression."
    }


# ============================================================
# PATTERN DISCOVERY
# ============================================================

def linear_fit(data):

    if len(data) < 2:
        return None

    try:

        x_values = [
            x for x, _ in data
        ]

        y_values = [
            y for _, y in data
        ]

        x_mean = (
            sum(x_values)
            / len(x_values)
        )

        y_mean = (
            sum(y_values)
            / len(y_values)
        )

        denominator = sum(
            (x - x_mean) ** 2
            for x in x_values
        )

        if denominator == 0:
            return None

        weight = sum(
            (x - x_mean)
            * (y - y_mean)
            for x, y in data
        ) / denominator

        bias = (
            y_mean
            - weight * x_mean
        )

        error = sum(
            abs(
                y
                - (
                    weight * x
                    + bias
                )
            )
            for x, y in data
        ) / len(data)

        return {
            "type":
                "linear",

            "weight":
                weight,

            "bias":
                bias,

            "error":
                error
        }

    except (TypeError, ZeroDivisionError):
        return None


def constant_fit(data):

    if not data:
        return None

    try:

        value = (
            sum(
                y for _, y in data
            )
            / len(data)
        )

        error = sum(
            abs(
                y - value
            )
            for _, y in data
        ) / len(data)

        return {
            "type":
                "constant",

            "value":
                value,

            "error":
                error
        }

    except (TypeError, ZeroDivisionError):
        return None


def solve_pattern(data):

    candidates = []

    constant = constant_fit(
        data
    )

    if constant is not None:
        candidates.append(
            constant
        )

    linear = linear_fit(
        data
    )

    if linear is not None:
        candidates.append(
            linear
        )

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda candidate:
            candidate["error"]
    )


# ============================================================
# CONCEPT EXTRACTION
# ============================================================

def extract_concept(
    task,
    strategy_type,
    result
):

    demand = task.get(
        "demand",
        ""
    )

    if strategy_type == "arithmetic":

        text = demand.lower()

        if (
            "*"
            in text
            or
            "×"
            in text
        ):

            return {
                "name":
                    "multiplication",

                "description":
                    "An arithmetic operation that "
                    "combines quantities through multiplication.",

                "category":
                    "arithmetic"
            }

        if (
            "/"
            in text
            or
            "÷"
            in text
        ):

            return {
                "name":
                    "division",

                "description":
                    "An arithmetic operation that "
                    "divides one quantity by another.",

                "category":
                    "arithmetic"
            }

        if "+" in text:

            return {
                "name":
                    "addition",

                "description":
                    "An arithmetic operation that "
                    "combines quantities into a total.",

                "category":
                    "arithmetic"
            }

        if "-" in text:

            return {
                "name":
                    "subtraction",

                "description":
                    "An arithmetic operation that "
                    "determines the difference between quantities.",

                "category":
                    "arithmetic"
            }

        return {
            "name":
                "arithmetic",

            "description":
                "Arithmetic expressions can be "
                "solved using mathematical operations.",

            "category":
                "arithmetic"
        }

    if strategy_type == "pattern":

        answer = result.get(
            "answer"
        )

        if isinstance(
            answer,
            dict
        ):

            pattern_type = answer.get(
                "type"
            )

            if pattern_type == "linear":

                return {
                    "name":
                        "linear_relationship",

                    "description":
                        "Some variables can be "
                        "represented by a linear relationship.",

                    "category":
                        "pattern"
                }

            if pattern_type == "constant":

                return {
                    "name":
                        "constant_relationship",

                    "description":
                        "Some datasets contain "
                        "an approximately constant output.",

                    "category":
                        "pattern"
                }

    return None


# ============================================================
# CONCEPT LEARNING
# ============================================================

def learn_concept(
    knowledge,
    concept_data,
    experience_id
):

    if concept_data is None:
        return None

    concept_name = concept_data["name"]

    existing = next(
        (
            concept
            for concept
            in knowledge["concepts"]
            if concept.get("name")
            == concept_name
        ),
        None
    )

    if existing is None:

        concept = {

            "name":
                concept_name,

            "description":
                concept_data["description"],

            "category":
                concept_data["category"],

            "times_observed":
                1,

            "experience_ids":
                [experience_id],

            "confidence":
                1.0
        }

        knowledge["concepts"].append(
            concept
        )

        return "NEW"

    existing["times_observed"] = (
        existing.get(
            "times_observed",
            0
        ) + 1
    )

    experience_ids = existing.setdefault(
        "experience_ids",
        []
    )

    if experience_id not in experience_ids:

        experience_ids.append(
            experience_id
        )

    old_confidence = existing.get(
        "confidence",
        1.0
    )

    existing["confidence"] = min(
        1.0,
        old_confidence + 0.05
    )

    return "REINFORCED"


# ============================================================
# STRATEGY MEMORY
# ============================================================

def strategy_record(
    knowledge,
    strategy_type
):

    existing = next(
        (
            strategy
            for strategy
            in knowledge["strategies"]
            if strategy.get("type")
            == strategy_type
        ),
        None
    )

    if existing is not None:

        existing.setdefault(
            "attempts",
            0
        )

        existing.setdefault(
            "successes",
            0
        )

        existing.setdefault(
            "failures",
            0
        )

        existing["success_rate"] = (
            calculate_success_rate(
                existing["successes"],
                existing["attempts"]
            )
        )

        return existing

    strategy = {

        "type":
            strategy_type,

        "attempts":
            0,

        "successes":
            0,

        "failures":
            0,

        "success_rate":
            0.0
    }

    knowledge["strategies"].append(
        strategy
    )

    return strategy


def strategy_score(
    knowledge,
    strategy_type
):

    strategy = strategy_record(
        knowledge,
        strategy_type
    )

    attempts = strategy["attempts"]

    success_rate = (
        strategy["success_rate"]
    )

    exploration_bonus = (
        0.25
        / math.sqrt(
            attempts + 1
        )
    )

    return (
        success_rate
        + exploration_bonus
    )


# ============================================================
# STRATEGY DISCOVERY
# ============================================================

def available_strategies(task):

    strategies = []

    demand = task.get(
        "demand"
    )

    if (
        isinstance(demand, str)
        and
        solve_arithmetic(
            demand
        ) is not None
    ):

        strategies.append(
            "arithmetic"
        )

    data = task.get(
        "data"
    )

    if data:

        strategies.append(
            "pattern"
        )

    return strategies


# ============================================================
# STRATEGY EXECUTION
# ============================================================

def execute_strategy(
    task,
    strategy_type
):

    if strategy_type == "arithmetic":

        return solve_arithmetic(
            task["demand"]
        )

    if strategy_type == "pattern":

        result = solve_pattern(
            task["data"]
        )

        if result is None:
            return None

        return {
            "answer":
                result,

            "reasoning":
                "Compared candidate patterns "
                "and selected the one with the "
                "lowest observed error."
        }

    return None


# ============================================================
# REASONING ENGINE
# ============================================================

def reason(
    knowledge,
    task
):

    candidates = available_strategies(
        task
    )

    if not candidates:

        return {
            "success":
                False,

            "answer":
                None,

            "reasoning":
                "MegaMind does not yet have "
                "a strategy capable of solving "
                "this input."
        }

    ranked_strategies = sorted(
        candidates,
        key=lambda strategy:
            strategy_score(
                knowledge,
                strategy
            ),
        reverse=True
    )

    for strategy_type in ranked_strategies:

        result = execute_strategy(
            task,
            strategy_type
        )

        if result is not None:

            return {

                "success":
                    True,

                "strategy":
                    strategy_type,

                "answer":
                    result["answer"],

                "reasoning":
                    result["reasoning"]
            }

    return {

        "success":
            False,

        "answer":
            None,

        "reasoning":
            "Available reasoning strategies "
            "failed to produce a valid result."
    }


# ============================================================
# EXPERIENCE LEARNING
# ============================================================

def learn_outcome(
    knowledge,
    task,
    result,
    success
):

    strategy_type = result.get(
        "strategy"
    )

    strategy = strategy_record(
        knowledge,
        strategy_type
    )

    strategy["attempts"] += 1

    if success:

        strategy["successes"] += 1

    else:

        strategy["failures"] += 1

    strategy["success_rate"] = (
        calculate_success_rate(
            strategy["successes"],
            strategy["attempts"]
        )
    )

    experience_id = (
        len(
            knowledge["experiences"]
        )
        + 1
    )

    experience = {

        "id":
            experience_id,

        "timestamp":
            now(),

        "demand":
            task.get("demand"),

        "context":
            task.get(
                "context",
                {}
            ),

        "strategy":
            strategy_type,

        "success":
            success,

        "answer":
            result.get(
                "answer"
            )
    }

    knowledge["experiences"].append(
        experience
    )

    concept_data = extract_concept(
        task,
        strategy_type,
        result
    )

    concept_result = learn_concept(
        knowledge,
        concept_data,
        experience_id
    )

    return concept_result


# ============================================================
# REASONING MODE
# ============================================================

def solve_mode(
    knowledge
):

    print()
    print(
        "MEGAMIND REASONING MODE"
    )

    print(
        "MegaMind will learn concepts "
        "automatically from experience."
    )

    print()

    demand = input(
        "Demand: "
    ).strip()

    context_text = input(
        "Context (optional): "
    ).strip()

    task = {

        "demand":
            demand,

        "context":
            (
                {
                    "description":
                        context_text
                }
                if context_text
                else {}
            )
    }

    data_text = input(
        "Pattern data x:y pairs "
        "(optional, e.g. 1:3,2:5,3:7): "
    ).strip()

    if data_text:

        try:

            pairs = []

            for item in data_text.split(","):

                parts = item.split(":")

                if len(parts) != 2:
                    raise ValueError

                x = float(
                    parts[0]
                )

                y = float(
                    parts[1]
                )

                pairs.append(
                    (x, y)
                )

            task["data"] = pairs

        except ValueError:

            print(
                "Invalid pattern format."
            )

            return

    result = reason(
        knowledge,
        task
    )

    print()
    print(
        "----- REASONING RESULT -----"
    )

    print(
        "Success:",
        result["success"]
    )

    print(
        "Strategy:",
        result.get(
            "strategy",
            "none"
        )
    )

    print(
        "Answer:",
        result.get(
            "answer"
        )
    )

    print(
        "Reasoning:",
        result["reasoning"]
    )

    if not result["success"]:

        print()
        print(
            "No learning update was made."
        )

        return

    feedback = input(
        "Was the output successful? (y/n): "
    ).strip().lower()

    success = (
        feedback == "y"
    )

    concept_result = learn_outcome(
        knowledge,
        task,
        result,
        success
    )

    save_knowledge(
        knowledge
    )

    print()

    if concept_result == "NEW":

        print(
            "MegaMind discovered a NEW concept."
        )

    elif concept_result == "REINFORCED":

        print(
            "MegaMind reinforced an existing concept."
        )

    else:

        print(
            "No concept was extracted."
        )

    print(
        "Experience learned and saved."
    )


# ============================================================
# PATTERN TRAINING MODE
# ============================================================

def pattern_training_mode(
    knowledge
):

    raw = input(
        "Enter x:y pairs, "
        "e.g. 1:3,2:5,3:7,4:9: "
    ).strip()

    try:

        data = []

        for item in raw.split(","):

            parts = item.split(":")

            if len(parts) != 2:
                raise ValueError

            x = float(
                parts[0]
            )

            y = float(
                parts[1]
            )

            data.append(
                (x, y)
            )

    except ValueError:

        print(
            "Invalid format."
        )

        return

    result = solve_pattern(
        data
    )

    if result is None:

        print(
            "MegaMind could not "
            "discover a pattern."
        )

        return

    print()
    print(
        "Candidate reasoning completed."
    )

    print(
        "Selected:",
        result
    )

    model = {
        key: value
        for key, value
        in result.items()
        if key != "error"
    }

    principle_type = (
        model["type"]
        + "_relationship"
    )

    principle = next(
        (
            p
            for p
            in knowledge["principles"]
            if p.get("type")
            == principle_type
        ),
        None
    )

    if principle is None:

        principle = {

            "type":
                principle_type,

            "description":
                "A reusable relationship "
                "discovered from data.",

            "instances":
                [],

            "times_discovered":
                0
        }

        knowledge["principles"].append(
            principle
        )

    duplicate = any(
        models_equal(
            instance.get("model"),
            model
        )
        for instance
        in principle["instances"]
        if isinstance(instance, dict)
    )

    if not duplicate:

        principle["instances"].append({

            "model":
                model,

            "average_error":
                result["error"]
        })

        principle["times_discovered"] += 1

        print(
            "NEW instance learned."
        )

    else:

        print(
            "Existing instance recognized."
        )

    knowledge["experiments"].append({

        "type":
            "pattern_discovery",

        "timestamp":
            now(),

        "training_examples":
            len(data),

        "discovered_pattern":
            model["type"],

        "model":
            model,

        "average_error":
            result["error"]
    })

    save_knowledge(
        knowledge
    )

    print(
        "Knowledge saved."
    )


# ============================================================
# KNOWLEDGE INSPECTION
# ============================================================

def inspect_knowledge(
    knowledge
):

    print()
    print(
        "===== MEGAMIND KNOWLEDGE ====="
    )

    print(
        "Principles:",
        len(
            knowledge["principles"]
        )
    )

    print(
        "Concepts:",
        len(
            knowledge["concepts"]
        )
    )

    print(
        "Experiences:",
        len(
            knowledge["experiences"]
        )
    )

    print(
        "Strategies:",
        len(
            knowledge["strategies"]
        )
    )

    print(
        "Experiments:",
        len(
            knowledge["experiments"]
        )
    )

    print()
    print(
        "CONCEPTS"
    )

    if not knowledge["concepts"]:

        print(
            "- No concepts learned yet."
        )

    else:

        for concept in knowledge["concepts"]:

            print(
                "-",
                concept.get(
                    "name",
                    "unknown"
                ),
                "| observations:",
                concept.get(
                    "times_observed",
                    0
                ),
                "| confidence:",
                round(
                    concept.get(
                        "confidence",
                        0.0
                    ),
                    2
                )
            )

    print()
    print(
        "STRATEGIES"
    )

    if not knowledge["strategies"]:

        print(
            "- No strategies learned yet."
        )

    else:

        for strategy in knowledge["strategies"]:

            print(
                "-",
                strategy.get(
                    "type",
                    "unknown"
                ),
                "| attempts:",
                strategy.get(
                    "attempts",
                    0
                ),
                "| success rate:",
                round(
                    strategy.get(
                        "success_rate",
                        0.0
                    ),
                    3
                )
            )

    print()
    print(
        "PRINCIPLES"
    )

    if not knowledge["principles"]:

        print(
            "- No principles learned yet."
        )

    else:

        for principle in knowledge["principles"]:

            print(
                "-",
                principle.get(
                    "type",
                    "unknown"
                ),
                "| instances:",
                len(
                    principle.get(
                        "instances",
                        []
                    )
                )
            )


# ============================================================
# MAIN
# ============================================================

def main():

    knowledge = load_knowledge()

    save_knowledge(
        knowledge
    )

    print()
    print(
        "=============================="
    )

    print(
        "          MEGAMIND"
    )

    print(
        "   SOVEREIGN REASONING CORE"
    )

    print(
        "       VERSION 5.1"
    )

    print(
        "=============================="
    )

    print()

    print(
        "Knowledge loaded."
    )

    print(
        "Principles:",
        len(
            knowledge["principles"]
        )
    )

    print(
        "Experiences:",
        len(
            knowledge["experiences"]
        )
    )

    print(
        "Strategies:",
        len(
            knowledge["strategies"]
        )
    )

    while True:

        print()
        print(
            "1. Reason about a demand"
        )

        print(
            "2. Learn a pattern"
        )

        print(
            "3. Inspect knowledge"
        )

        print(
            "4. Exit"
        )

        choice = input(
            "Choose an option: "
        ).strip()

        if choice == "1":

            solve_mode(
                knowledge
            )

        elif choice == "2":

            pattern_training_mode(
                knowledge
            )

        elif choice == "3":

            inspect_knowledge(
                knowledge
            )

        elif choice == "4":

            print()
            print(
                "MegaMind shutting down."
            )

            break

        else:

            print(
                "Invalid choice."
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()
