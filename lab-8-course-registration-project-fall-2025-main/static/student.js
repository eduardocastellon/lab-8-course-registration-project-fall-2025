// Helper function to format dates array to days string (e.g., [0,1,0,1,0] -> "T Th")
function formatDays(datesArray) {
    const dayAbbrevs = ['M', 'T', 'W', 'Th', 'F'];
    const days = [];
    for (let i = 0; i < 5; i++) {
        if (datesArray[i] === 1) {
            days.push(dayAbbrevs[i]);
        }
    }
    return days.length > 0 ? days.join(' ') : 'TBA';
}

// Helper function to format date range display
function formatDateRange(startDate, endDate) {
    if (startDate && endDate) {
        return `Start: ${startDate} | End: ${endDate}`;
    } else if (startDate) {
        return `Start: ${startDate}`;
    } else if (endDate) {
        return `End: ${endDate}`;
    }
    return 'Dates: TBA';
}

//get student id to see whos logged in else go back to sign in
document.addEventListener("DOMContentLoaded", async()=>{
    const studentId = localStorage.getItem("student_id");
    if(!studentId){
        window.location.href="/";
        return;
    }
    const signoutLink=document.querySelector(".signout");
    const tabs = document.querySelectorAll(".tab");
    const tabContents = document.querySelectorAll(".tab-content");

    const welcomeEl = document.getElementById("welcome");
    const yourTbody=document.getElementById("users_courses_row");
    const addTbody = document.getElementById("add_courses_row");

    if(signoutLink){
        signoutLink.addEventListener("click", (e)=>{
            e.preventDefault();
            localStorage.removeItem("student_id");
            window.location.href="/";
        });
    }

    //buttons for add course and users courses
    tabs.forEach((tab) => {
        tab.addEventListener("click", ()=>{
            const targetId=tab.getAttribute("data-target");
            tabs.forEach((t)=> t.classList.remove("active"));
            tab.classList.add("active");

            tabContents.forEach((content)=>{
                if(content.id === targetId){
                    content.style.display="block";
                    content.classList.add("active");
                }
                else{
                    content.style.display="none";
                    content.classList.remove("active");
                }
            });
        });
    });
    try{
        //get student and courses info
        const [studentRes, coursesRes] = await Promise.all([
            fetch(`/students/${studentId}`), fetch("/courses"),
        ]);

        const studentData=await studentRes.json();
        const courses = await coursesRes.json();

        //welcome the user 
        if (welcomeEl && studentData.first_name){
            welcomeEl.textContent=`Welcome, ${studentData.first_name}!`;
        }

        const registeredDict = studentData.registered_courses || {};
        const registeredIds = Object.keys(registeredDict);
        const myCourses = courses.filter((c)=> registeredIds.includes(c.unique_id));
        const addableCourses = courses.filter((c)=> !registeredIds.includes(c.unique_id) && c.registered_students < c.capacity);
        
        //show courses
        yourTbody.innerHTML = "";
        if(myCourses.length === 0){
            const row=document.createElement("tr");
            row.innerHTML='<td colspan="6">You are not registered in any courses yet.</td>';
            yourTbody.appendChild(row);
        }
        else{
            myCourses.forEach((course)=>{
                const row = document.createElement("tr");
                const enrolledText = `${course.registered_students} / ${course.capacity}`;
                const dropBtnCell = document.createElement("td");
                const dropBtn = document.createElement("button");

                dropBtn.className = "icon-btn";
                dropBtn.textContent = "−";
                dropBtn.title = "Drop this course";
                dropBtn.style.color = "#ff4444";
                dropBtn.style.fontWeight = "bold";

                dropBtn.addEventListener("click", () => {
                    if(confirm(`Are you sure you want to drop ${course.course_name}?`)){
                        dropCourse(course.unique_id);
                    }
                });

                dropBtnCell.appendChild(dropBtn);
                const daysText = formatDays(course.dates || [0, 0, 0, 0, 0]);
                const dateRange = formatDateRange(course.start_date, course.end_date);
                row.innerHTML=`
                    <td>${course.course_name}</td>
                    <td>${course.instructor}</td>
                    <td>
                        <div style="margin-bottom: 4px;"><strong style="font-size: 1.1em;">${daysText}</strong></div>
                        <div style="color: #0066cc; font-size: 0.9em; font-weight: 600;">${dateRange}</div>
                    </td>
                    <td>${course.time}</td>
                    <td>${enrolledText}</td>`;
                row.appendChild(dropBtnCell);
                yourTbody.appendChild(row);
            });
        }
        //enroll into course
        async function enrollInCourse(uniqueId){
            try{
                const res=await fetch(`/students/${studentId}/courses/${uniqueId}`,{method:"PUT"});
                const data = await res.json();
                
                if(res.ok){
                    alert("you have enrolled into the course");
                    window.location.reload();
                }
                else{
                    alert(data.message || "Could not enroll in course.");
                }

            }
            catch(err){
                console.error(err);
                alert("cant connect to server when enrolling");
            }
        }

        //drop course
        async function dropCourse(uniqueId){
            try{
                const res=await fetch(`/students/${studentId}/courses/${uniqueId}`,{method:"DELETE"});
                const data = await res.json();
                
                if(res.ok){
                    alert("You have dropped the course");
                    window.location.reload();
                }
                else{
                    alert(data.message || "Could not drop course.");
                }

            }
            catch(err){
                console.error(err);
                alert("cant connect to server when dropping course");
            }
        }

        //show  the added courses
        addTbody.innerHTML="";
        if(addableCourses.length === 0){
            const row = document.createElement("tr");
            row.innerHTML ='<td colspan="6">No courses available to add right now.</td>';
            addTbody.appendChild(row);
        }
        else{
            addableCourses.forEach((course)=>{
                const row= document.createElement("tr");
                const enrolledText = `${course.registered_students} / ${course.capacity}`;
                const btnCell=document.createElement("td");
                const btn= document.createElement("button");

                btn.className = "icon-btn";
                btn.textContent= "+";
                btn.title = "Add this class";

                btn.addEventListener("click", ()=> {
                    enrollInCourse(course.unique_id);
                });

                btnCell.appendChild(btn);
                const daysText = formatDays(course.dates || [0, 0, 0, 0, 0]);
                const dateRange = formatDateRange(course.start_date, course.end_date);
                row.innerHTML=`
                    <td>${course.course_name}</td>
                    <td>${course.instructor}</td>
                    <td>
                        <div style="margin-bottom: 4px;"><strong style="font-size: 1.1em;">${daysText}</strong></div>
                        <div style="color: #0066cc; font-size: 0.9em; font-weight: 600;">${dateRange}</div>
                    </td>
                    <td>${course.time}</td>
                    <td>${enrolledText}</td>`;
                
                row.appendChild(btnCell);
                addTbody.appendChild(row);
            });
        }
    }
    catch(err){
        console.error("Error loading student or courses:", err);
        if(yourTbody){
            const row = document.createElement("tr");
            row.innerHTML='<td colspan="4">Error loading data try again.</td>';
            yourTbody.appendChild(row);
        }
    }
});