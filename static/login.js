//load page
document.addEventListener("DOMContentLoaded", () =>{
    const form = document.getElementById("login_page");
    const errorlogin = document.getElementById("login_error");



    //check if button is presed
    form.addEventListener("submit", async (e) =>{
        e.preventDefault();

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        //for error
        errorlogin.textContent="";
        errorlogin.style.color="#d21f1fff";

        //send login to backend
        try{
            const res = await fetch("/login", {
                method: "POST",
                headers: {"Content-Type": "application/json"}, 
                body: JSON.stringify({ username, password})
            });
            const data = await res.json();
            
            //check if 200 code go to student login if a student
            if(res.ok){
                if(data.status === "STUDT"){
                    localStorage.setItem("student_id", data.id);
                    window.location.href="/student";
                }
                else if(data.status === "TEACH"){
                    localStorage.setItem("instructor_id", data.id)
                    window.location.href="/instructor";
                }
                else if(data.status === "ADMIN"){
                    window.location.href="/admin";
                }
                else{
                    alert("not a student account")
                }
                console.log("Login succcess:", data);
                errorlogin.style.color = "rgba(12, 244, 12, 1)";
                errorlogin.textContent = "Login successful";
            }
            //else bad pass or user
            else{
                errorlogin.textContent= data.message || "invalid username or password";
            }
        }catch(err){
            console.error(err);
            errorlogin.textContent="error connecting to server"
        }
        
    });
});
const sparkle_amount = 10;
const fly = 80;

//when mouse move create sparkle
document.addEventListener('mousemove', (e) => {
    for (let i = 0; i < sparkle_amount; i++) {
        createSparkle(e.clientX, e.clientY);
    }
});

function createSparkle(x, y) {
    const sparkle = document.createElement('div');
    sparkle.className = 'sparkle';

    //color sparkles
    const hue = Math.floor(Math.random() * 360);
    sparkle.style.color = `hsl(${hue}, 100%, 70%)`;
    sparkle.style.background = `hsl(${hue}, 100%, 70%)`;

    //begins on cursor
    sparkle.style.left = x + 'px';
    sparkle.style.top = y + 'px';

    //random direction & distance to fly 
    const angle = Math.random() * Math.PI*2;
    const distance = Math.random() * fly;
    const dx = Math.cos(angle) * distance;
    const dy = Math.sin(angle) * distance;

    //allows the sparks to fly out a little
    sparkle.style.setProperty('--start-x', '-50%');
    sparkle.style.setProperty('--start-y', '-50%');
    sparkle.style.setProperty('--end-x', `calc(-50% + ${dx}px)`);
    sparkle.style.setProperty('--end-y', `calc(-50% + ${dy}px)`);

    document.body.appendChild(sparkle);

    //remove sparkle
    setTimeout(() => {
        sparkle.remove();
    }, 800);
}
