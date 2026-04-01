import { SidebarNav } from "@/components/sidebar-nav";
import { Header } from "@/components/header";
import { ChatSidebar } from "@/components/chat-sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <SidebarNav />
      <div className="flex flex-1 flex-col lg:pl-64">
        <Header />
        <main className="flex-1 px-4 py-6 lg:px-8 lg:py-8">{children}</main>
      </div>
      <ChatSidebar />
    </div>
  );
}
