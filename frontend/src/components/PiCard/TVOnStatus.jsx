// components/PiCard/TVOnStatus.jsx

const TVOnStatus = ({ tvStatus }) => {
  return (
    <div className={`text-center w-full`}>
      <p
        className={`w-fit m-auto text-slate-100 ${
          tvStatus ? "bg-emerald-600" : "bg-rose-600"
        } py-1 px-4 rounded-full`}
      >
        TV : {tvStatus ? "On" : "Off"}
      </p>
    </div>
  );
};

export default TVOnStatus;
