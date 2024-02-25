import { Navigate, Outlet } from "react-router-dom";
import { useContext } from "react";
import AuthContext from "../context/AuthContext";


const StudentRoutes = (children, ...rest) => {
    let {user} = useContext(AuthContext)
    console.log("user.is_student: "+user.is_student)
    return(
        user.is_student ? <Outlet/> : <Navigate to="/login" />
        // user ? <Outlet/> : <Outlet/>
    )
}

export default StudentRoutes