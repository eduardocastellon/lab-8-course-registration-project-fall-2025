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
            
            //check if 200 code if so show message login success
            if(res.ok){
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
