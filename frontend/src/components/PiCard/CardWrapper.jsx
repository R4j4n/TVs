import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { RefreshCw } from 'lucide-react'

export function CardWrapper({ pi, status, error, onRefresh, children }) {


  return (
    <Card className="w-full drop-shadow-lg">
      <CardHeader className="space-y-1">
        <div className="flex items-center justify-between overflow-hidden">
          <CardTitle className="w-1/2 text-xl font-bold">{pi.name}  </CardTitle>
          {status ? <div className="w-1/4 text-center text-slate-200 justify-end h-100% rounded-full bg-emerald-600 transition-all ease-in duration-[1] ">Active</div> :
            <div className="w-1/4 text-center text-slate-200 justify-end h-100% rounded-full bg-rose-600 transition-all ease-in duration-[1] ">Inactive</div>
          }<Button 
            variant="ghost" 
            size="icon"
            onClick={onRefresh}
            className="w-1/4"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {children}
      </CardContent>
    </Card>
  )
}