# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

I think the three main things a user should be able to do in PawPal+ are enter their own info and their pet's info, add care tasks, and generate a plan for the day.

For the first one, the owner would put in their name, how much time they have available each day, and any preferences they have. They would then add a pet with basic details like its name and species.

Next, the user should be able to add tasks such as a walk, a feeding, or a medication and give each one a duration and a priority, so the app knows how long it takes and how important it is. They should also be able to edit or remove a task later on if something changes.

Lastly, the user should be able to ask the app to build today's schedule. The app would fit the most important tasks into the time the owner has and show them in order, along with an explanation of why each task was picked and when it happens.

**a. Initial design**

My initial UML design has four classes, which are Owner, Pet, Task, and Scheduler. An Owner has one or more pets, each Pet has its own list of tasks, and the Scheduler uses the Owner to get to all of the pets and their tasks when it builds a plan.

The Owner class holds the owner's name, how many minutes they have available in a day, when their day starts, and their preferences. It is also responsible for keeping track of their pets, so it can add or remove a pet and gather the tasks from all of them into one list.

The Pet class holds basic details like the pet's name, species, and age, along with the tasks that pet needs. Its job is mostly to add, remove, and return those tasks.

The Task class represents one care activity, such as a walk or a feeding. It stores the title, how long it takes, its priority, a category, an optional preferred time, how often it repeats, and whether it has been completed. It can mark itself as complete and turn its priority into a number so that tasks are easier to sort.

The Scheduler class is where the actual planning happens. It sorts the tasks by priority, filters out the ones that do not fit in the owner's available time, checks for tasks whose times overlap, and then builds the final plan as an ordered list of start times, tasks, and reasons. It can also explain the plan so the owner understands why each task was picked. I used dataclasses for Task, Pet, and Owner since they mainly hold data, as opposed to the Scheduler, which is mostly logic.

**b. Design changes**

Yes, my design changed after I had the AI review the skeleton in pawpal_system.py. I made three changes based on what it pointed out.

The first change was keeping track of which pet each task belongs to. Originally get_all_tasks() just returned one flat list of tasks, which meant that if an owner had two dogs, the plan would only say "Morning walk" without saying which dog it was for. I changed it to return each task paired with its pet, and the plan entries now include the pet as well.

The second change was adding two small helpers to the Scheduler that convert a time like "08:30" into minutes since midnight and back. I was storing times as "HH:MM" strings, which are easy to read but hard to add durations to or compare when checking for overlaps. This way the owner still sees normal times, as opposed to the Scheduler, which does its math on plain numbers.

The third change was replacing the completed flag on Task with a last_completed date and adding an is_due() method. With only a true or false value, a daily task would stay marked as done forever, and a weekly task had no way of knowing whether it was due today. Storing the last date it was done lets the Scheduler figure that out.

The AI also suggested a few smaller cleanups, like checking that priority is a valid value, but I decided to leave those for later since they did not affect the overall structure.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
