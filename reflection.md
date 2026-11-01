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

Later on, when I added recurring tasks, I changed the Task class again. The assignment wanted a new task to be created each time a daily or weekly task is completed, so I replaced last_completed with a due_date and a completed flag. Now when a task is marked done, the Scheduler makes a copy of it that is due the next day or the next week and adds it back to the pet. I also renamed the method that cuts tasks to fit the owner's time to fit_to_budget(), so that filter_tasks() could be used for filtering by pet and status instead. The final version of the design is in diagrams/uml_final.mmd.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers how many minutes the owner has available, the priority of each task, whether a task has a preferred time, and whether the task is actually due today. A task that is already done or is not due until later in the week is left out of the plan, and any task that is overdue still gets included.

I decided that priority should matter the most, since some tasks like medication can affect a pet's health if they get skipped, as opposed to something like brushing that can wait a day. The owner's available time is treated as a hard limit, because the plan is not useful if it asks for more time than the owner has. Preferred times come next, since a lot of pet care happens at set times, like feeding or giving meds, so I place those tasks exactly at their time and fit the flexible ones around them. The owner preferences field is in the Owner class, but in the end the scheduler does not use it, since I could not think of a preference that the priority and preferred time did not already cover.

**b. Tradeoffs**

One tradeoff my scheduler makes is how it decides which tasks fit in the owner's available time. It goes through the tasks from highest to lowest priority and keeps each one if there is still enough time left, and if a task does not fit, it skips it and moves on to the next one. This means it does not try every possible combination to find the one that uses the most time. For example, with 90 minutes available it might skip a 45 minute bath and fill the time with smaller tasks instead, even if a different mix would have used the time a bit better.

I think this is reasonable for a pet owner since the most important tasks, like medication or a walk, always get picked first, and the result is easy to explain. If the app told someone it dropped their dog's walk to squeeze in two grooming tasks because the math worked out better, that would be confusing. A pet owner only has a handful of tasks in a day, so the small amount of time that might be wasted is not really an issue.

Another smaller tradeoff is that when two tasks with set times overlap, the scheduler only shows a warning as opposed to moving one of them. I decided to leave that choice to the owner, since they know which task can actually be moved.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code in VS Code for most of the project, which included brainstorming the classes, writing the skeleton, implementing the scheduling logic, writing the tests, and connecting everything to the Streamlit app. Early on I told it to stop and ask me whenever it reached a decision, so that I was the one choosing how the system worked as opposed to it making those choices on its own.

The features that helped the most were the skeleton review and having the AI run and check its own work. The review in Phase 1 pointed out that tasks did not know which pet they belonged to and that doing math on "HH:MM" strings would be a problem, which saved me from finding those issues later. Running main.py, pytest, and a headless version of the app after each change also caught real bugs, like two identical tasks being counted as one when the scheduler worked out which tasks were skipped.

The most helpful prompts were the ones where I asked for a few options with the tradeoffs laid out, such as how to place tasks on the clock or how to store recurring tasks. Seeing the options side by side made it easy to pick the one that fit my design.

I kept everything in one chat, but I treated each phase like its own session. Each one started with only that phase's instructions and ended with a commit, so I always knew what the current goal was and what had already been finished. This kept the planning for one phase from mixing with another, like keeping the testing work separate from the scheduling logic.

**b. Judgment and verification**

One suggestion I did not accept as-is was in Phase 4, when I asked the AI how detect_conflicts() could be simplified. It suggested using itertools.combinations to loop over every pair of tasks, which is more Pythonic, but it is harder to follow if you do not already know that function, and it was not any faster. I decided to keep my nested loops since they make it clear how the pairs are formed. For the open slot method I did take its simpler version, since that one was both shorter and easier to read. I also turned down a few of the smaller cleanups from the skeleton review, like validating the priority value, since they did not change the structure of the system.

To verify what the AI suggested, I ran main.py and the tests after each change and checked that the output made sense. When the open slot method was rewritten, I also tested it with a few cases, like busy times that were out of order or overlapping, to make sure it still picked the right start times.

---

## 4. Testing and Verification

**a. What you tested**

I tested the main behaviors of the scheduler, which were sorting, recurring tasks, conflict detection, and fitting tasks into the owner's available time. For sorting, I checked that tasks come back in order by time with the flexible ones at the end, and that the final plan is in time order. For recurring tasks, I checked that completing a daily task creates a new one for the next day, a weekly task comes back in seven days, and a one-time task does not repeat. For conflicts, I tested two tasks at the exact same time and two tasks that overlap, and I also made sure that back-to-back tasks, like a walk ending at 8:30 and breakfast starting at 8:30, are not flagged.

I also added a few edge cases, like an owner with no pets, a pet with no tasks, and an owner with zero minutes available, to make sure the app gives an empty plan as opposed to crashing. These tests were important since the scheduler makes a lot of small decisions on its own, and a mistake in one of them, like a task repeating on the wrong day, would be easy to miss just by looking at the output. I used a fixed date in the tests so they give the same result no matter what day they are run.

**b. Confidence**

I would give my scheduler a 4 out of 5. All 21 tests pass, and they cover the behaviors I think matter most to a pet owner. I am not fully confident yet since the Streamlit side of the app is not covered by any automated tests, and the app does not check for bad input, such as a misspelled priority or a time typed in the wrong format.

If I had more time, I would test what happens when a schedule runs past midnight, since the time math currently assumes everything happens in one day. I would also test a task that is longer than the owner's whole day and a weekly task that is completed late, to see if the next due date still makes sense.

---

## 5. Reflection

**a. What went well**

I am most satisfied with how the scheduler explains itself. Every task in the plan has a short reason next to it, tasks that did not fit are listed as opposed to just disappearing, and overlapping times show up as a warning. I think that makes the app feel more trustworthy to a pet owner, since they can see why the plan looks the way it does. I am also happy with the recurring tasks, since marking a walk as done in the app actually creates tomorrow's walk.

**b. What you would improve**

If I had another iteration, I would add input validation, so a misspelled priority or a badly typed time gives a clear error. I would also either use the owner preferences field or remove it, since right now it does not do anything. Another thing is that removing a task removes every task with that title, which includes its completed history, so I would change it to remove only the one the user clicked. In hindsight, I would also save the data to a file, since everything is lost when the Streamlit session ends.

**c. Key takeaway**

The main thing I learned is that being the lead architect means making the design decisions yourself, even when the AI can write the code faster than you can. The AI was very good at writing and testing code once I knew what I wanted, but questions like how recurring tasks should work or whether a simpler version was actually easier to read still needed me to decide. Having a clear UML and skeleton before any real code was written also made it much easier to tell when a suggestion did not fit the design.
