//get student id to see whos logged in else go back to sign in
document.addEventListener("DOMContentLoaded", async()=>{
    const studentID = localStorage.getItem("student_id");
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
            tab.classList.add("Active");

            tabContents.forEach((content)=>{
                if(content.id === targetId){
                    content.computedStyleMap.display="black";
                    content.classList.add("active");
                }
                else{
                    content.computedStyleMap.display="none";
                    content.classList.remove("active");
                }
            });
        });
    });
    try{
        //get student and courses info
        const [studentRes, coursesRes] = await Promise.all([
            fetch(`/student/${studentID}`), fetch("/courses"),
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
            row.innerHTML='<td colspan="4">You are not registered in any courses yet.</td>';
            yourTbody.appendChild(row);
        }
        else{
            myCourses.forEach((course)=>{
                const row = document.createElement("tr");
                const enrolledText = `${course.registered_students} / ${course.capacity}`;

                row.innerHTML=`
                    <td>${course.course_name}</td>
                    <td>${course.instructor}</td>
                    <td>${course.time}</td>
                    <td>${enrolledText}</td>`;
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

        //show  the added courses
        addTbody.innerHTML="";
        if(addableCourses.length === 0){
            const row = document.createElement("tr");
            row.innerHTML ='<td colspan="5">No courses available to add right now.</td>';
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
                    if(course.registered_students >= course.capacity){
                        alert("class is full")
                    }
                    else{
                        enrollInCourse(course.unique_id);
                    }
                });

                btnCell.appendChild(btn);
                row.innerHTML=`
                    <td>${course.course_name}</td>
                    <td>${course.instructor}</td>
                    <td>${course.time}</td>
                    <td>${enrolledText}</td>`;
                
                row.appendChild(btnCell);
                addTbody.appendChild(btnCell);
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