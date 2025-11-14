document.addEventListener("DOMContentLoaded", async () => {
    //gets instructor id if no id go back to login
    const instructorId= localStorage.getItem("instructor_id");
    if(!instructorId){
        window.location.href="/";
        return;
    }

    const signout = document.querySelector(".signout");
    if(signout){
        //when signout button is clicked clear the id and go back to login
        signout.addEventListener("click", (e) => {
            localStorage.removeItem("instructor_id");
            window.location.href="/";
        });
    }

    //grabs data
    const welcomeEl = document.getElementById("welcome");
    const tbody = document.getElementById("instructor-courses-body");

    try{
        const [instrRes, coursesRes] = await Promise.all([
            fetch(`/instructors/${instructorId}`),
            fetch("/courses")
        ]);

        //convert http response to json
        const instructor = await instrRes.json();
        const allCourses = await coursesRes.json();

        welcomeEl.textContent=`welcome ${instructor.first_name}!`;
        const assignedIds = instructor.assigned_courses || [];
        
        //gets instructors courses  only
        const instructorCourses = allCourses.filter(c =>assignedIds.includes(c.unique_id));

        tbody.innerHTML="";
        
        instructorCourses.forEach((course) => {
            const row = document.createElement("tr");
            row.style.cursor="pointer";

            //fills the rows with the course info
            row.innerHTML=`
                <td>${course.course_name}</td>
                <td>${course.instructor}</td>
                <td>${course.time}</td>
                <td>${course.registered_students}/${course.capacity}</td>`;
            
            //makes the rows clickable directs them to the grades for students
            row.addEventListener("click", () => {
                window.location.href=`/instructor/course/${course.unique_id}`;
            });
            tbody.appendChild(row);
        });
    }
    catch(err){
        console.error(err);
        tbody.innerHTML=`<tr><td colspan="4">Error loading data.</td></tr>`;
    }
});