import { DashboardLayout } from '@/components/dashboard/dashboard-layout'
import React from 'react'

const DashboardLayoutWrapper = ({ children }: { children: React.ReactNode }) => {
    return (
        <DashboardLayout userRole="admin">
            {children}
        </DashboardLayout>
    )
}

export default DashboardLayoutWrapper