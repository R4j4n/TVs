"use client";

import { isTVOn } from "@/lib/api";
import { useEffect, useState } from "react";

const TVOnStatus = ({ host }) => {
    const [TVOn, setTVOn] = useState(false);

    const checkTVStatus = async (host) => {
        try { 
            const TVStatus = await isTVOn(host);
            if (TVStatus.status === "on"){
                setTVOn(true);
            }
            else{
                setTVOn(false);
            }
        } catch (error) {
            console.log("Unable to check if tv is on or off: ", error)
        }
    }
    useEffect(() => {
        checkTVStatus(host);
        setTimeout(() => {}, 30000);
    },)
    


    return <div className={`text-center w-full`}>
        <p className={`w-fit m-auto text-slate-100 ${TVOn? "bg-emerald-600" : "bg-rose-600"} py-1 px-4 rounded-full`}>
            TV : {TVOn ? "On" : "Off"}
            </p>
            </div>;
};

export default TVOnStatus;
