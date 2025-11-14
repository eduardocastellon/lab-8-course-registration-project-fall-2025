document.addEventListener("DOMContentLoaded", async () => {
    const signout = document.querySelector(".signout");
    if(signout){
        signout.addEventListener("click", (e)=>{
            e.preventDefault();
            localStorage.removeItem("instructor_id");
            window.location.href="/";
        });
    }
    const backBtn = document.getElementById("back");
    if(backBtn){
        backBtn.addEventListener("click", ()=>{
            window.location.href="/instructor";
        });
    }

    const courseUid = window.location.pathname.split("/").pop();
    const courseTitleEl = document.getElementById("course-title");
    const rosterBody = document.getElementById("roster-body");

    try{
        const [coursesRes, studentsRes] = await Promise.all([
            fetch("/courses"),
            fetch("/students"),
        ]);

        const courses = await coursesRes.json();
        const students = await studentsRes.json();
        const course = courses.find((c) => c.unique_id === courseUid);

        if(course && courseTitleEl){
            courseTitleEl.textContent=course.course_name;
        }
        rosterBody.innerHTML="";

        const enrolled = students.filter((s) => {
            const reg = s.registered_courses || {};
            return Object.prototype.hasOwnProperty.call(reg, courseUid);
        });
        if(enrolled.length === 0){
            const row = document.createElement("tr");
            row.innerHTML ='<td colspan="2">No students enrolled in this course.</td>';
            rosterBody.appendChild(row);
            return;
        }

        enrolled.forEach((student) => {
            const reg=student.registered_courses || {};
            const grade = reg[courseUid];
            const row = document.createElement("tr");

            row.innerHTML=`<td>${student.first_name} ${student.last_name}</td>
                <td><input type="number" min="0" max="100"></td>`;
            const gradeInput = row.querySelector("input");

            if(typeof grade === "number"){
                gradeInput.value = grade;
            }
            
            gradeInput.addEventListener("change", async () => {
                const newGrade=parseInt(gradeInput.value, 10);
                if(Number.isNaN(newGrade)){
                    alert("enter a valid number");
                }
                try{
                    const res = await fetch(`/students/${student.id}/courses/${courseUid}/grades/${newGrade}`,{ method : "PUT" });
                    if(!res.ok){
                        const data = await res.json().catch(() => ({}));
                        console.error("Grade update failed:", data);
                        alert(data.message || "Error updating grade.");
                    }
                    else{
                        console.log(`updated grade for student ${student.id} in course ${courseUid} to ${newGrade}`);
                    }
                }
                catch(err){
                    console.error(err);
                    alert("cant connect to server, grade update");
                }
            });
            rosterBody.appendChild(row);
        });
    }
    catch(err){
        console.error(err);
        if(rosterBody){
            const row = document.createElement("tr");
            row.innerHTML='<td colspan="2">Error loading roster. Please refresh.</td>';
            rosterBody.appendChild(row);
        }
    }
});