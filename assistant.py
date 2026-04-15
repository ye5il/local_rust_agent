import os
import subprocess
import re
from rich.console import Console
from rich.syntax import Syntax

console = Console()

class MinimalAssistant:
    def __init__(self):
        self.model = "qwen2.5-coder:7b"
        self.suggestion = ""
        # --- 100 ITEM KNOWLEDGE BASE ---
        self.kb = {
            "E0382": "Variable moved! Solution: Use .clone() or borrow with & reference.",
            "E0499": "Multiple mutable borrows! Scope them or use a single mutable ref.",
            "E0502": "Cannot borrow as mutable while immutable refs exist. Finish using & first.",
            "E0507": "Cannot move out of a reference. Use .clone() or take ownership.",
            "E0594": "Cannot assign to immutable variable. Add 'mut' keyword.",
            "E0596": "Cannot borrow immutable as mutable. Declare variable as 'mut'.",
            "E0716": "Temporary value dropped while still borrowed. Extend its lifetime.",
            "borrow": "Rule: 1 mutable OR many immutable references. Never both.",
            "move": "Primitives (i32, bool) are copied; Strings/Vecs are moved by default.",
            "clone_perf": "Don't .clone() everywhere; it's expensive. Use references (&) for read-only.",
            "deref": "Use '*' to access the value behind a pointer/reference.",
            "shadowing": "Shadowing (let x = x + 1) is fine for type conversion, but don't overdo it.",
            "binding": "Use 'ref' in match patterns to avoid moving the value.",
            "box": "Use Box<T> to store large data on the heap instead of the stack.",
            "rc": "Use Rc<T> for multiple-ownership in single-threaded scenarios.",
            "arc": "Use Arc<T> for thread-safe shared ownership.",
            "cell": "Use Cell or RefCell for internal mutability (mutating inside &self).",
            "cow": "Use Cow<'a, str> to avoid allocation when data is mostly read-only.",
            "leak": "Memory leaks possible via ref cycles. Use Weak<T>.",
            "drop": "Rust handles drop automatically; manual drop(x) is rare.",
            "E0308": "Type mismatch! Expected X, found Y. Check function signatures.",
            "E0425": "Value not found in this scope. Check imports or spelling.",
            "E0433": "Undeclared type/module. Did you miss a 'use' statement?",
            "E0277": "Trait not implemented! E.g., Struct needs 'Display' to be printed.",
            "E0605": "Invalid cast. Use 'as' carefully or use TryInto trait.",
            "i32_vs_isize": "Use i32 for data, isize for indexing collections (Vec, Array).",
            "str_vs_string": "&str is a slice (fixed), String is owned (growable).",
            "option_none": "Always handle 'None' case when working with Options.",
            "result_err": "Always handle 'Err' case when working with Results.",
            "turbofish": "Use ::<T> syntax when compiler can't infer type.",
            "unit_type": "() is the unit type. It's like 'void' but actually a value.",
            "as_ref": "Use .as_ref() to convert Option<String> to Option<&str>.",
            "into": "Use .into() for clean type conversions (e.g., &str to String).",
            "from": "Implementing From<T> automatically gives you Into<T>.",
            "panic": "panic!() stops thread. Use only for unrecoverable errors.",
            "todo": "todo!() is for prototyping; it compiles but panics at runtime.",
            "unimplemented": "Signals a feature isn't ready yet.",
            "reachable": "unreachable!() tells compiler code path is impossible.",
            "const_vs_static": "const is inlined; static has a fixed memory address.",
            "enums": "Rust enums are Algebraic Data Types; use for state machines.",
            "read_line": "BUG: read_line() appends! Always call buf.clear() in loops.",
            "trim": "trim() returns a ref. Use .to_string() to own data.",
            "parse": "parse() needs hint or turbofish: .parse::<i32>().",
            "format": "format!() is the easiest way to concat strings.",
            "concat": "Adding strings: s1 + &s2. s1 moves, s2 borrows.",
            "bytes": "Use .as_bytes() for low-level byte manipulation.",
            "chars": "Iterate with .chars(), not by index (UTF-8 issues).",
            "expect": "Better than unwrap(); describes WHY it might fail.",
            "stdin": "stdin() is buffered. Use lock() for performance.",
            "stdout": "println!() is slow for heavy output; use BufWriter.",
            "file_open": "Check if file exists before opening to avoid panics.",
            "path": "Use std::path::PathBuf for cross-platform paths.",
            "flush": "Manual flush() needed if using print! before input.",
            "write": "Implement std::fmt::Display for custom formatting.",
            "debug": "Use #[derive(Debug)] and {:?} for logging.",
            "to_owned": "Use .to_owned() instead of .clone() for &str -> String.",
            "escapes": "Use raw strings r#\"...\"# to ignore backslashes.",
            "vec_capacity": "Vec::with_capacity(n) prevents reallocations.",
            "vec_pop": ".pop() returns Option; handle empty case.",
            "vec_macro": "vec![val; n] creates vector with 'n' copies.",
            "iter": ".iter() borrows, .iter_mut() borrows mutably.",
            "into_iter": ".into_iter() consumes collection (moves).",
            "map": ".map() is lazy; call .collect() to execute.",
            "filter": ".filter() takes a ref to item: |&x| x > 0.",
            "collect": "Specify target type: .collect::<Vec<_>>().",
            "fold": "Use .fold() for accumulating values.",
            "find": ".find() returns first match as Option.",
            "any_all": ".any() and .all() are short-circuiting.",
            "enumerate": "Gives (index, value) pairs in loops.",
            "zip": "Combines two iterators into one of pairs.",
            "flat_map": "Flatten nested collections while iterating.",
            "cloned_iter": "Use .cloned() to convert refs to values in iter.",
            "sum_perf": ".iter().sum() is highly optimized.",
            "closures": "Use 'move' keyword to capture by ownership.",
            "laziness": "Rust iterators are zero-cost abstractions.",
            "chain": "Append one iterator to another.",
            "rev": ".rev() reverses double-ended iterators.",
            "position": "Returns index of first match.",
            "take_skip": ".take(n) and .skip(n) for pagination.",
            "collect_result": "Iterator<Result> -> Result<Vec> is possible.",
            "unsafe": "Use unsafe { } only for FFI or extreme performance.",
            "ffi": "extern 'C' allows calling C code.",
            "repr_c": "Use #[repr(C)] for FFI struct compatibility.",
            "raw_pointers": "*const T and *mut T have no safety guarantees.",
            "threads": "std::thread::spawn requires 'Send' + 'static.",
            "mutex": "Mutex<T> for thread-safe mutability via .lock().",
            "rwlock": "RwLock<T> allows many readers OR one writer.",
            "sync_send": "Send = transferable; Sync = shareable via refs.",
            "channels": "Use mpsc for thread communication.",
            "async": "Requires a runtime like 'tokio'.",
            "futures": "Futures are lazy state machines.",
            "zero_cost": "What you don't use, you don't pay for.",
            "macro_rules": "Declarative macros generate code at compile time.",
            "proc_macros": "Procedural macros are compiler plugins.",
            "attribute": "#[inline] or #[no_mangle] guide compiler.",
            "mod_system": "Use 'mod' to declare, 'use' to import.",
            "pub_visibility": "Items are private by default; use 'pub'.",
            "traits_dyn": "Box<dyn Trait> for runtime polymorphism.",
            "traits_impl": "impl Trait for compile-time dispatch.",
            "standard_lib": "The 'std' library is small but powerful."
        }

    def check_rust(self, code):
        with open("temp.rs", "w", encoding="utf-8") as f:
            f.write(code)
        res = subprocess.run(["rustc", "temp.rs", "--out-dir", "./", "--color", "never"], 
                             capture_output=True, text=True)
        for f in ["temp.rs", "temp", "temp.exe"]:
            if os.path.exists(f): 
                try: os.remove(f)
                except: pass
        return res.returncode == 0, res.stderr

    def get_hints(self, text):
        return "\n".join([f"- {v}" for k, v in self.kb.items() if k in text])

    def deep_fix(self, code, task):
        current_code = code
        for attempt in range(1, 4):
            is_ok, err = self.check_rust(current_code)
            hints = self.get_hints(err if not is_ok else task)
            
            prompt = f"""Senior Rust Engineer. Fix Task: {task}
Code: {current_code}
Error: {err if not err else 'None'}
Hints: {hints}
Return only the fixed code in a ```rust block."""
            
            result = subprocess.run(["ollama", "run", self.model, prompt], capture_output=True, text=True, encoding="utf-8")
            code_match = re.search(r"```rust\n(.*?)\n```", result.stdout, re.DOTALL)
            new_code = code_match.group(1).strip() if code_match else current_code
            
            if self.check_rust(new_code)[0]: return new_code
            current_code = new_code
        return current_code

    def run(self, file_path):
        if not os.path.exists(file_path): return
        while True:
            console.clear()
            with open(file_path, "r", encoding="utf-8") as f: source = f.read()
            console.print(Syntax(source, "rust", theme="monokai", line_numbers=True))
            
            if self.suggestion:
                console.print("\n[bold green]>>> Proposed Fix:[/bold green]")
                console.print(Syntax(self.suggestion, "rust", theme="monokai"))
                if console.input("\nSave changes? (y/n): ").lower() == 'y':
                    with open(file_path, "w", encoding="utf-8") as f: f.write(self.suggestion)
                self.suggestion = ""; continue

            cmd = console.input("\nprompt: ").strip()
            if cmd.lower() in ["exit", "quit"]: break
            with console.status("[magenta]Fixing...[/magenta]"):
                self.suggestion = self.deep_fix(source, cmd)

if __name__ == "__main__":
    path = input("File (.rs): ")
    MinimalAssistant().run(path)