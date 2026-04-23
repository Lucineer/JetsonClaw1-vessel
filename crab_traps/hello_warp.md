# Crab Trap: Hello Warp!

**Level:** Absolute Beginner  
**Time:** 20-30 minutes  
**Prerequisites:** None (first time with warp-as-room)  
**Goal:** Create and run your first warp room

## 🎯 **WELCOME!**

This is your very first crab trap. No prior experience needed. In 20-30 minutes, you'll create a simple warp room that says "Hello!" and learn the basic concepts.

### **What You'll Build:**
A "hello room" that:
1. Takes a name as input
2. Says hello to that name
3. Runs on GPU (even if you don't have one yet - we'll simulate)
4. Teaches you the warp-as-room basics

### **What You'll Learn:**
- What a "room" is in warp-as-room architecture
- How rooms work together in "warps"
- Basic GPU concepts (simulated for now)
- How to compile and run your first room

## 🛠️ **SETUP (2 MINUTES)**

### **You Need:**
- A computer (any kind)
- A text editor (VS Code, Notepad, anything)
- Basic command line knowledge (how to type commands)

### **No GPU Required:**
We'll simulate GPU execution for this first trap. Real GPU comes later!

### **Files You'll Create:**
- `hello_room.cu` - Your first room
- `hello_warp.cu` - The warp that runs your room
- `run_hello.sh` - Script to compile and run

## 📝 **STEP 1: CREATE YOUR FIRST ROOM (5 MINUTES)**

### **What's a Room?**
A room is a specialized function that does one thing well. Your hello room will take a name and say hello.

### **Create hello_room.cu:**
```c
// hello_room.cu
// Your first warp room!

#include <stdio.h>

// Simple room that says hello
void hello_room(const char* name, char* greeting) {
    // Create greeting
    sprintf(greeting, "Hello, %s! Welcome to warp-as-room!", name);
    
    // That's it! Your room is done.
    // Rooms can be this simple or much more complex.
}
```

### **Save this file as `hello_room.cu`**

**What this does:**
- Takes a `name` (input)
- Creates a `greeting` (output)
- Uses standard C - no GPU code yet
- Simple and understandable

## 🚀 **STEP 2: CREATE A WARP (5 MINUTES)**

### **What's a Warp?**
A warp is a group of 32 rooms working together. For now, we'll create a simple warp that runs one room.

### **Create hello_warp.cu:**
```c
// hello_warp.cu
// A warp that runs hello rooms

#include <stdio.h>

// Include your room
void hello_room(const char* name, char* greeting);

int main() {
    printf("=== Hello Warp Starting ===\n");
    
    // Test names
    const char* names[] = {
        "Alice",
        "Bob", 
        "Charlie",
        "Diana"
    };
    
    // Greetings storage
    char greetings[4][100];
    
    // Run rooms (simulated warp)
    printf("Running rooms in warp...\n");
    for (int i = 0; i < 4; i++) {
        hello_room(names[i], greetings[i]);
        printf("Room %d: %s\n", i, greetings[i]);
    }
    
    printf("=== Hello Warp Complete ===\n");
    printf("You just ran 4 rooms in a simulated warp!\n");
    
    return 0;
}
```

### **Save this as `hello_warp.cu`**

**What this does:**
- Creates 4 "rooms" (hello_room calls)
- Runs them in a loop (simulating warp execution)
- Prints the results
- Shows how warps coordinate multiple rooms

## ⚡ **STEP 3: COMPILE AND RUN (3 MINUTES)**

### **Create run_hello.sh:**
```bash
#!/bin/bash
# run_hello.sh - Compile and run your first warp

echo "Compiling your first warp..."

# Compile (using gcc since we're simulating)
gcc -o hello_warp hello_warp.cu hello_room.cu

echo "Running your first warp..."
echo ""

./hello_warp

echo ""
echo "🎉 CONGRATULATIONS! You just ran your first warp!"
```

### **Make it executable and run:**
```bash
chmod +x run_hello.sh
./run_hello.sh
```

### **Expected Output:**
```
=== Hello Warp Starting ===
Running rooms in warp...
Room 0: Hello, Alice! Welcome to warp-as-room!
Room 1: Hello, Bob! Welcome to warp-as-room!
Room 2: Hello, Charlie! Welcome to warp-as-room!
Room 3: Hello, Diana! Welcome to warp-as-room!
=== Hello Warp Complete ===
You just ran 4 rooms in a simulated warp!

🎉 CONGRATULATIONS! You just ran your first warp!
```

## 🎨 **STEP 4: MAKE IT YOUR OWN (5 MINUTES)**

### **Customize Your Room:**
Edit `hello_room.cu` to make it personal:

```c
// Customized hello room
void hello_room(const char* name, char* greeting) {
    // Add your own style
    sprintf(greeting, "👋 Hey %s! Ready to build amazing things with warp-as-room?", name);
    
    // Or add more logic
    if (name[0] == 'A') {
        sprintf(greeting + strlen(greeting), " (A-names are awesome!)");
    }
}
```

### **Add More Rooms:**
Create a second room in the same file:

```c
// Second room: goodbye room
void goodbye_room(const char* name, char* farewell) {
    sprintf(farewell, "Goodbye, %s! Come back and build more rooms soon!", name);
}
```

### **Update the warp to use both:**
```c
// In hello_warp.cu, add:
void goodbye_room(const char* name, char* farewell);

// And in main():
char farewells[4][100];
for (int i = 0; i < 4; i++) {
    goodbye_room(names[i], farewells[i]);
    printf("Goodbye %d: %s\n", i, farewells[i]);
}
```

## 📊 **STEP 5: UNDERSTAND WHAT YOU BUILT (5 MINUTES)**

### **Key Concepts Learned:**

1. **Room:** A specialized function (hello_room, goodbye_room)
2. **Warp:** A group of rooms working together (hello_warp runs multiple rooms)
3. **Input/Output:** Rooms take inputs (names), produce outputs (greetings)
4. **Coordination:** Warps coordinate when and how rooms run
5. **Simulation:** We simulated GPU execution - real GPU comes next!

### **The Warp-as-Room Architecture:**
- **Real warps:** 32 rooms running simultaneously on GPU
- **Real coordination:** Rooms share data instantly within warp
- **Real speed:** Thousands of rooms running in milliseconds
- **What you built:** The conceptual foundation

### **From Simulation to Real GPU:**
- **This trap:** CPU simulation, understandable concepts
- **Next trap (TensorRT Dojo):** Real GPU, actual performance
- **After that:** Optimization, real-world applications

## 🏆 **STEP 6: CHALLENGE YOURSELF**

### **Beginner Challenges:**
1. Add a third room that counts letters in the name
2. Make the warp run different rooms for different names
3. Add command-line arguments for custom names
4. Create a simple visualization of the warp execution

### **Intermediate Challenges:**
1. Convert to actual CUDA code (add `__global__` keyword)
2. Make rooms run in parallel (simulate with threads)
3. Add timing to measure performance
4. Create a Makefile for automated compilation

### **Ready for More?**
You've completed your first crab trap! You now understand:
- What rooms and warps are
- How to create and run them
- The basic architecture

## 🔗 **STEP 7: WHAT'S NEXT**

### **Your Learning Path:**
1. ✅ **This trap:** Hello Warp! (concepts, simulation)
2. → **Next:** TensorRT Dojo (real GPU, actual performance)
3. → **Then:** Warp API Workshop (coordination, optimization)
4. → **After:** Choose your application domain

### **Immediate Next Steps:**
1. **Celebrate!** You built your first warp room
2. **Share!** Tell someone what you built
3. **Continue!** Move to the TensorRT Dojo
4. **Join!** The community is waiting for you

### **Community Resources:**
- **GitHub:** See more examples and projects
- **Matrix Chat:** Ask questions, get help
- **PLATO:** Share your rooms when ready
- **Documentation:** Learn more about each concept

## 🎉 **CONGRATULATIONS!**

You've completed your first crab trap! You now know:

✅ What a warp room is  
✅ How to create and run rooms  
✅ The basic warp-as-room architecture  
✅ How to customize and extend rooms  
✅ What comes next in your learning journey

**You're officially a warp-as-room developer!**

**Next stop: TensorRT Dojo for real GPU execution and performance.** 🚀

---

*This crab trap is designed for absolute beginners.*  
*No prior GPU or CUDA knowledge required.*  
*Built by the community for the community.*  
*Special welcome to our newest warp developer!*
