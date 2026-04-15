fn main() {
    let name = String::from("Gemini");
    
    // Fixed Ownership Move
    say_hello(name.clone());

    // 'name' is now valid here, but we can't use clone to print it again
    
    // Fixed Type Mismatch
    let sum = add_numbers(5, 10);
    println!("Toplam: {}", sum);
}

fn say_hello(n: String) {
    println!("Selam, {}!", n);
}

fn add_numbers(a: i32, b: i32) -> i32 {
    a + b
}