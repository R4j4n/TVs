// components/PiCard/CardWrapper.jsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import TVOnStatus from "./TVOnStatus";

export function CardWrapper({
  pi,
  title,
  status,
  error,
  tvStatus,
  onRefresh,
  isGroup = false,
  children,
}) {
  return (
    <Card
      className={`w-full drop-shadow-lg ${
        !status ? "bg-red-400/20" : ""
      } hover:drop-shadow-xl `}
    >
      <CardHeader className="space-y-1">
        <div className="flex flex-col items-center justify-between overflow-hidden">
          <CardTitle className="w-1/2 text-xl font-bold">
            {isGroup ? title : pi?.name}
          </CardTitle>
          <div className="w-full flex justify-between items-center">
            <div className={`flex ${isGroup ? "justify-center w-full": "justify-start w-[78%]"} items-center mx-auto pt-4`}>
          { !isGroup &&  <TVOnStatus tvStatus={tvStatus} /> }
          {status ? (
            <div className= {`${ isGroup?"text-center": "text-left"} text-slate-200 justify-end h-100% px-4 py-1 rounded-full bg-emerald-600 transition-all ease-in duration-[1] `}>
              Active
            </div>
          ) : (
            <div className= {`${ isGroup?"text-center": "text-left"} text-slate-200 justify-end h-100% rounded-full px-4 py-1 bg-rose-600 transition-all ease-in duration-[1]`}>
              Inactive
            </div>
          )}

          
          </div>
          {onRefresh && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onRefresh()}
              className="w-1/4"
            >
              <RefreshCw className="h-4 w-4 mt-4" />
            </Button>
          )}
         </div> 
        </div>
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </CardHeader>
      <CardContent className="space-y-4">{children}</CardContent>
    </Card>
  );
}