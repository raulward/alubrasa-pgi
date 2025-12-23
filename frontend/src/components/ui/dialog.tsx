
import { ReactNode } from "react";

const Dialog = ({ children }: { children: ReactNode }) => <div>{children}</div>
const DialogTrigger = ({ children }: { children: ReactNode }) => <button>{children}</button>
const DialogContent = ({ children }: { children: ReactNode }) => <div>{children}</div>
const DialogHeader = ({ children }: { children: ReactNode }) => <div>{children}</div>
const DialogFooter = ({ children }: { children: ReactNode }) => <div>{children}</div>
const DialogTitle = ({ children }: { children: ReactNode }) => <h3>{children}</h3>
const DialogDescription = ({ children }: { children: ReactNode }) => <p>{children}</p>
const DialogOverlay = ({ children }: { children: ReactNode }) => <div>{children}</div>
const DialogPortal = ({ children }: { children: ReactNode }) => <div>{children}</div>
const DialogClose = ({ children }: { children: ReactNode }) => <div>{children}</div>

export {
    Dialog,
    DialogTrigger,
    DialogContent,
    DialogHeader,
    DialogFooter,
    DialogTitle,
    DialogDescription,
    DialogOverlay,
    DialogPortal,
    DialogClose
}
